"""Read-only unified conversation inventory; never create or resume sessions."""
import re
import local_conversation
import task_bridge

def history():
    items, errors = [], []
    try:
        goals = {g['id']: g['title'] for g in task_bridge.goals()}
        for s in task_bridge.remote('/api/chat/sessions').get('sessions', []):
            sid = s.get('session_id', '')
            if not re.fullmatch(r'[a-f0-9]{32}', sid): continue
            agent = s.get('agent_id') or 'codex'
            items.append({'id': sid, 'title': goals.get(s.get('goal_id'), s.get('goal_id') or 'Conversation'),
                          'agent': 'Claude' if agent == 'claude-code' else agent,
                          'updated_at': s.get('last_activity_at') or s.get('updated_at') or s.get('created_at') or ''})
    except Exception:
        errors.append('Historique LoopX momentanément inaccessible.')
    for file in local_conversation.ROOT.glob('*.json'):
        if not re.fullmatch(r'[a-f0-9]{32}', file.stem): continue
        try:
            d = local_conversation.load(file.stem)
            s, messages = d['session'], d.get('messages', [])
            title = next((m['text'].strip().splitlines()[0][:90] for m in messages if m.get('role') == 'user' and m.get('text', '').strip()), 'Nouvelle conversation')
            items.append({'id': file.stem, 'title': title, 'agent': ('M2' if s.get('destination') == 'm2' else 'Ollama') + ' · ' + s.get('model', ''), 'updated_at': messages[-1].get('created_at', '') if messages else ''})
        except (ValueError, OSError, KeyError, TypeError):
            errors.append('Une conversation locale ne peut pas être lue.')
    return {'items': sorted(items, key=lambda s: s['updated_at'], reverse=True), 'errors': sorted(set(errors))}
