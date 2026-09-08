"""Durable Ollama conversations. No tools, task execution or automatic retries."""
import json
import threading
import urllib.request
import uuid
from pathlib import Path
from task_bridge import atomic, now, identifier
ROOT = Path(__file__).resolve().parent / 'task-data' / 'conversations'
LOCK = threading.RLock()

def path(sid):
    return ROOT / (identifier(sid) + '.json')

def exists(sid):
    return path(sid).is_file()

def load(sid):
    with LOCK:
        return json.loads(path(sid).read_text())

def create(model, goal):
    sid = uuid.uuid4().hex
    data = {'session': {'session_id': sid, 'agent_id': 'ollama', 'model': model, 'goal_id': goal, 'destination': 'ollama', 'active_turn_id': None}, 'messages': [], 'turn_ids': []}
    with LOCK: atomic(path(sid), data)
    return data

def append(data, role, text):
    data['messages'].append({'message_id': uuid.uuid4().hex, 'created_at': now(), 'role': role, 'text': text})

def send(sid, text, tid, context):
    with LOCK:
        data = load(sid)
        if tid in data['turn_ids']: return data
        if data['session']['active_turn_id']: raise ValueError('Une réponse est déjà en cours')
        data['turn_ids'].append(tid)
        append(data, 'user', text)
        data['session']['active_turn_id'] = tid
        atomic(path(sid), data)
    threading.Thread(target=complete, args=(sid, context), daemon=True).start()
    return data

def complete(sid, context):
    data = load(sid)
    prompt = [{'role': 'system', 'content': 'Réponds en français. Tu es un chat sans outils : ne prétends jamais avoir exécuté une tâche. Mesures horodatées du dashboard : ' + json.dumps(context, ensure_ascii=False)}]
    prompt += [{'role': 'assistant' if m['role'] == 'agent' else 'user', 'content': m['text']} for m in data['messages'] if m['role'] in {'user', 'agent'}]
    try:
        request = urllib.request.Request('http://127.0.0.1:11434/api/chat', data=json.dumps({'model': data['session']['model'], 'messages': prompt, 'stream': False, 'keep_alive': '5m'}).encode(), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=180) as response: result = json.load(response)
        answer = result.get('message', {}).get('content')
        if not answer: raise ValueError('Le modèle n’a pas renvoyé de texte')
        append(data, 'agent', answer)
    except Exception as error:
        append(data, 'error', 'Réponse interrompue : ' + str(error))
    with LOCK:
        data['session']['active_turn_id'] = None
        atomic(path(sid), data)

def recover():
    for file in ROOT.glob('*.json'):
        data = json.loads(file.read_text())
        if data['session']['active_turn_id']:
            append(data, 'error', 'Serveur redémarré pendant la réponse. Aucun message renvoyé automatiquement.')
            data['session']['active_turn_id'] = None
            atomic(file, data)
