"""Dashboard integration with LoopX's durable, idempotent task actions.

LoopX owns execution. This module stores receipts and reports, never replays
historical tasks and never treats an agent reply as proof of task success.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'task-data'
REGISTRY = Path(os.environ.get('STATION_LOOPX_REGISTRY', str(Path.home() / '#DEV/_Agents/loopx/workspace/.loopx/registry.json')))
NOTEPLAN = Path(os.environ.get('STATION_NOTEPLAN_ROOT', str(Path.home() / 'Library/Containers/co.noteplan.NotePlan-setapp/Data/Library/Application Support/co.noteplan.NotePlan-setapp')))
LOOPX = 'http://127.0.0.1:8870'
LOCK = threading.RLock()
TERMINAL = {'response_received', 'failed'}

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def atomic(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    tmp.chmod(0o600)
    tmp.replace(path)

def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', value):
        raise ValueError('Identifiant invalide')
    return value

def remote(path, body=None):
    req = urllib.request.Request(LOOPX + path,
        data=None if body is None else json.dumps(body).encode(),
        headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        payload = json.load(error)
        gate = payload.get('gate') or {}
        raise ValueError(gate.get('next_action') or payload.get('error') or str(error)) from error
    if payload.get('ok') is False:
        raise ValueError(payload.get('error', 'Erreur LoopX'))
    return payload

def goals():
    registry = json.loads(REGISTRY.read_text())
    return [{'id': g['id'], 'title': g.get('display_name', g['id']), 'project': g.get('repo', '')}
            for g in registry.get('goals', []) if g.get('status') == 'active']

def load(key):
    return json.loads((DATA / (identifier(key) + '.json')).read_text())

def save(job):
    job['updated_at'] = now()
    atomic(DATA / (job['id'] + '.json'), job)

def jobs():
    with LOCK:
        return sorted([json.loads(p.read_text()) for p in DATA.glob('*.json')], key=lambda j: j['created_at'], reverse=True)

def notes(query=''):
    """Read unchecked task lines only; never writes to the NotePlan vault."""
    results = []
    started = time.monotonic()
    for folder in ('Notes', 'Calendar'):
        base = NOTEPLAN / folder
        if not base.is_dir():
            continue
        for directory, dirs, names in os.walk(base, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith(('.', '@')) and not d.endswith('_attachments') and d not in {'node_modules', 'venv', 'Backups', 'Caches'}]
            if time.monotonic() - started > 8:
                return {'items': results, 'truncated': True}
            candidates = []
            for name in names:
                if Path(name).suffix.lower() in {'.md', '.txt'}:
                    candidates.append(Path(directory) / name)
            for path in candidates:
                if time.monotonic() - started > 8:
                    return {'items': results, 'truncated': True}
                if path.is_symlink() or not path.is_file() or path.suffix.lower() not in {'.md', '.txt'}:
                    continue
                if not path.resolve().is_relative_to(NOTEPLAN.resolve()) or '@Archive' in path.parts or path.stat().st_size > 1_000_000:
                    continue
                for number, line in enumerate(path.read_text(errors='replace').splitlines(), 1):
                    match = re.match(r'^\s*[-*]\s+\[ \]\s+(.+)', line)
                    if not match:
                        continue
                    text = match.group(1)
                    rel = str(path.relative_to(NOTEPLAN))
                    if query and query.casefold() not in (text + rel).casefold():
                        continue
                    token = hashlib.sha256((rel + ':' + str(number) + ':' + text).encode()).hexdigest()
                    results.append({'id': token, 'text': text, 'note': rel, 'line': number})
                    if len(results) == 200:
                        return {'items': results, 'truncated': True}
    return {'items': results, 'truncated': False, 'available': NOTEPLAN.is_dir()}

def preview(body):
    key = identifier(body.get('id'))
    text = str(body.get('text', '')).strip()
    if not text or len(text) > 6000:
        raise ValueError('Saisis une tâche de 1 à 6000 caractères')
    goal = next((g for g in goals() if g['id'] == body.get('goal_id')), None)
    if not goal:
        raise ValueError('Projet LoopX inconnu')
    with LOCK:
        if (DATA / (key + '.json')).exists():
            existing = load(key)
            if existing['text'] != text or existing['goal_id'] != goal['id']:
                raise ValueError('Cet identifiant appartient à une autre demande')
            if existing['status'] != 'preparing':
                return existing
            return prepare(existing)
        job = {'id': key, 'goal_id': goal['id'], 'project': goal['project'], 'text': text,
               'source': str(body.get('source', 'Saisie directe'))[:500], 'status': 'preparing',
               'created_at': now(), 'result': '', 'error': '', 'archive': ''}
        save(job)
    # The same key can recover a lost preview response without creating a new task.
    return prepare(job)

def prepare(job):
    request = {'action_kind': 'todo.create', 'summary': 'Exécuter la tâche du dashboard',
        'normalized_parameters': {'goal_id': job['goal_id'], 'text': job['text'],
                                  'agent_id': 'codex', 'start_execution': True},
        'context': {'kind': 'goal', 'goal_id': job['goal_id']}, 'idempotency_key': 'station-' + job['id']}
    proposal = remote('/api/actions/preview', request)['proposal']
    with LOCK:
        job.update(proposal_id=proposal['proposal_id'], status='preview', error='')
        save(job)
    return job

def apply(key):
    with LOCK:
        job = load(key)
        if job['status'] != 'preview':
            return job
        job['status'] = 'dispatching'
        save(job)
    # Never automatically repeat apply after an uncertain network response.
    try:
        response = remote('/api/actions/' + identifier(job['proposal_id']) + '/apply', {})
        accept(job, response['proposal'])
    except Exception as error:
        with LOCK:
            job.update(status='uncertain', error='Envoi à vérifier : ' + str(error))
            save(job)
    return job

def accept(job, proposal):
    ids = (proposal.get('receipt') or {}).get('resource_ids') or {}
    with LOCK:
        if ids.get('session_id') and ids.get('turn_id'):
            job.update(session_id=ids['session_id'], turn_id=ids['turn_id'], todo_id=ids.get('todo_id'), status='running', error='')
        elif proposal.get('status') in {'failed', 'gated', 'stale', 'cancelled'}:
            job.update(status='failed', error=json.dumps(proposal.get('failure') or proposal.get('gate') or proposal.get('stale') or proposal['status'], ensure_ascii=False))
        else:
            job.update(status='uncertain', error='LoopX ne confirme pas encore le démarrage. Aucun nouvel envoi automatique.')
        save(job)

def validate(key, note):
    """An explicit operator validation, separate from the agent's claim."""
    note = str(note or '').strip()
    if not 1 <= len(note) <= 500:
        raise ValueError('Indique la preuve vérifiée (500 caractères maximum)')
    with LOCK:
        job = load(key)
        if job.get('validation'):
            return job
        if job['status'] != 'response_received' or not job.get('todo_id'):
            raise ValueError('Une réponse d’exécution est nécessaire avant validation')
    proposal = remote('/api/actions/preview', {
        'action_kind': 'todo.update', 'summary': 'Valider le résultat vérifié',
        'normalized_parameters': {'goal_id': job['goal_id'], 'todo_id': job['todo_id'],
            'operation': 'complete', 'note': note, 'agent_id': 'codex', 'no_followup': True},
        'context': {'kind': 'goal', 'goal_id': job['goal_id']}, 'idempotency_key': 'validate-' + job['id']})['proposal']
    result = remote('/api/actions/' + identifier(proposal['proposal_id']) + '/apply', {})
    if result['proposal']['status'] != 'applied':
        raise ValueError('La clôture n’est pas confirmée par LoopX')
    with LOCK:
        job['validated_at'] = now()
        job['validation'] = note
        job['validation_receipt'] = result['proposal'].get('receipt')
        save(job)
    return job

def archive(job):
    from unification_view import REPO
    if not REPO.is_dir():
        raise ValueError('Clone Unification absent : résultat conservé localement')
    path = REPO / 'chats' / ('station-' + job['id'] + '.md')
    path.parent.mkdir(exist_ok=True)
    content = '# Tâche station — ' + job['id'] + '\n\n'
    content += '\n'.join(['- Date : ' + job['created_at'], '- Objectif : ' + job['goal_id'],
        '- Session LoopX : ' + job.get('session_id', 'indisponible'), '- Tour : ' + job.get('turn_id', 'indisponible'),
        '- État : ' + job['status'], '- Source : ' + job['source'],
        '- Lien local : http://127.0.0.1:8871/execution#' + job['id'],
        '- Deeplink Codex : indisponible, non inventé.', '- Git : aucun commit ni push automatique.'])
    content += '\n\n## Synthèse en trois lignes\n'
    content += 'Demande : ' + ' '.join(job['text'].split())[:220] + '\n\n'
    content += 'Exécution : ' + ('réponse reçue de Codex.' if job['status'] == 'response_received' else 'échec signalé.') + '\n\n'
    content += 'Intégration : résultat archivé ; validation métier restant à vérifier.\n'
    content += '\n## Demande\n' + job['text'] + '\n\n## Résultat de l’agent (déclaration, pas validation indépendante)\n' + (job['result'] or job['error']) + '\n'
    if path.exists() and path.read_text() != content:
        raise ValueError('Une fiche différente existe déjà ; elle est conservée')
    if not path.exists():
        path.write_text(content)
    subprocess.run([sys.executable, str(REPO / 'scripts/update_index.py')], check=True, timeout=30, capture_output=True)
    job['archive'] = 'chats/' + path.name
    job['archive_error'] = ''

def reconcile(job):
    if job['status'] in {'dispatching', 'uncertain'} and job.get('proposal_id'):
        accept(job, remote('/api/actions/' + identifier(job['proposal_id']))['proposal'])
    if job['status'] == 'running':
        snapshot = remote('/api/chat/sessions/' + identifier(job['session_id']))
        messages = [m for m in snapshot.get('messages', []) if m.get('turn_id') == job['turn_id']]
        errors = [m for m in messages if m.get('role') == 'error']
        replies = [m for m in messages if m.get('role') == 'agent']
        if errors:
            job.update(status='failed', error=str(errors[-1].get('text', 'Erreur agent')))
        elif replies and not snapshot.get('session', {}).get('active_turn_id'):
            job.update(status='response_received', result=str(replies[-1].get('text', '')))
        elif snapshot.get('session', {}).get('last_error_code'):
            job.update(status='failed', error=str(snapshot['session']['last_error_code']))
        save(job)
    if job.get('validation') and job.get('archive') and not job.get('validation_archived'):
        from unification_view import REPO
        path = REPO / job['archive']
        marker = '\n## Validation opérateur — ' + job['id'] + '\n'
        content = path.read_text()
        if marker not in content:
            path.write_text(content + marker + '\n' + job['validation'] + '\n\nClôture confirmée par le reçu LoopX.\n')
        job['validation_archived'] = True
        save(job)
    if job['status'] in TERMINAL and not job.get('archive'):
        try:
            archive(job)
        except Exception as error:
            job['archive_error'] = str(error)
        save(job)

def worker():
    while True:
        for job in jobs():
            if job['status'] in {'running', 'dispatching', 'uncertain'} or (job['status'] in TERMINAL and not job.get('archive')) or (job.get('validation') and not job.get('validation_archived')):
                try:
                    reconcile(job)
                except Exception as error:
                    job['error'] = 'Suivi indisponible : ' + str(error)
                    save(job)
        time.sleep(5)

def start():
    threading.Thread(target=worker, daemon=True, name='station-result-monitor').start()
