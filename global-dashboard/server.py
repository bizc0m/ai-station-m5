#!/usr/bin/env python3
"""Local dashboard: read service state and open explicitly selected tools."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import re
import task_bridge
from unification_view import render as render_unification
from legacy_actions import LaunchMixin, LAUNCHERS
import os
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
STATION = ROOT.parent
PORT = 8871
SERVICES = {
    'loopx': ('LoopX', 'http://127.0.0.1:8870/status.json', 'http://127.0.0.1:8870/chat/'),
    'ollama': ('Ollama', 'http://127.0.0.1:11434/api/tags', 'http://127.0.0.1:11434/api/tags'),
    'comfyui': ('ComfyUI', 'http://127.0.0.1:8188/system_stats', 'http://127.0.0.1:8188/'),
    'm2': ('M2 · Osaurus', 'http://100.90.189.76:1338/health', 'http://100.90.189.76:1338/'),
}
AGENTS = [
    ('codex', 'Codex', '/Applications/ChatGPT.app/Contents/Resources/codex', 'LoopX + terminal', []),
    ('claude', 'Claude Code', '/Users/JOB/.local/bin/claude', 'LoopX + terminal', []),
    ('aider', 'Aider', '/Users/JOB/.local/bin/aider', 'Terminal · modèle local 14B', ['--model', 'ollama/qwen2.5-coder:14b', '--no-auto-commits']),
    ('opencode', 'OpenCode', '/Users/JOB/.local/bin/opencode', 'Terminal · configuration existante', []),
    ('hermes', 'Hermes', '/Users/JOB/.local/bin/hermes', 'Terminal · modèle local 8B', ['-m', 'qwen3:8b']),
    ('ollama', 'Ollama', '/opt/homebrew/bin/ollama', 'Terminal · modèle local 8B', ['run', 'qwen3:8b']),
]
CACHE = {'time': 0, 'data': None}
LOCK = threading.Lock()

def probe(entry):
    name, endpoint, url = entry
    started = time.monotonic()
    result = {'name': name, 'url': url, 'available': False, 'detail': 'Non vérifié'}
    try:
        with urllib.request.urlopen(endpoint, timeout=3) as response:
            body = response.read(6_000_001)
            if len(body) > 6_000_000:
                raise ValueError('Réponse trop volumineuse')
            result['code'] = response.status
            try:
                data = json.loads(body)
            except (ValueError, UnicodeDecodeError):
                data = None
            result.update(available=200 <= response.status < 300, detail=f'HTTP {response.status}', data=data)
            if isinstance(data, dict) and data.get('ok') is False:
                result.update(available=False, detail='Le service signale une erreur')
    except urllib.error.HTTPError as error:
        result.update(code=error.code, detail=f'HTTP {error.code}')
    except (OSError, ValueError) as error:
        result['detail'] = 'Aucune réponse sous 3 s' if isinstance(error, (TimeoutError, socket.timeout)) else 'Service inaccessible'
    result['elapsed_ms'] = round((time.monotonic() - started) * 1000)
    return result

def snapshot():
    with LOCK:
        if CACHE['data'] and time.monotonic() - CACHE['time'] < 5:
            return CACHE['data']
        with ThreadPoolExecutor(max_workers=4) as pool:
            measured = dict(zip(SERVICES, pool.map(probe, SERVICES.values())))
        measured['comfyui']['outputs_available'] = Path('/Users/JOB/#DEV/02-apps/ComfyUI-output').is_dir()
        raw = measured['loopx'].get('data') or {}
        goals = []
        for item in raw.get('attention_queue', {}).get('items', []):
            asset = item.get('project_asset') or {}
            todos = asset.get('agent_todos') or {}
            goals.append({'id': item['goal_id'], 'open': todos.get('open', 0), 'done': todos.get('done', 0),
                          'tasks': [{'text': t.get('text', ''), 'id': t.get('todo_id'), 'status': t.get('status', 'open')} for t in todos.get('items', [])]})
        models = []
        for model in (measured['ollama'].get('data') or {}).get('models', []):
            models.append({'name': model.get('name', ''), 'gb': round(model.get('size', 0) / 1_000_000_000, 1)})
        for item in measured.values():
            item.pop('data', None)
        result = {'checked_at': datetime.now().astimezone().isoformat(timespec='seconds'), 'host': socket.gethostname(),
                  'services': measured, 'goals': goals, 'models': models,
                  'agents': [{'id': key, 'name': name, 'installed': os.access(binary, os.X_OK), 'mode': mode} for key, name, binary, mode, args in AGENTS]}
        CACHE.update(time=time.monotonic(), data=result)
        return result

def command_for(key):
    import shlex
    for agent_id, name, binary, mode, args in AGENTS:
        if key == agent_id:
            if not os.access(binary, os.X_OK):
                raise ValueError('Cet agent n’est pas installé')
            return '#!/bin/zsh\ncd /Users/JOB/\\#DEV || exit 1\nexec ' + shlex.join([binary, *args]) + '\n'
    raise ValueError('Agent inconnu')

class Handler(LaunchMixin, BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        return self.respond(payload, status)

    def respond(self, body, status=200, content_type='application/json; charset=utf-8'):
        payload = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(payload)

    def local(self):
        host = self.headers.get('Host', '')
        return self.client_address[0] == '127.0.0.1' and host in {f'127.0.0.1:{PORT}', f'localhost:{PORT}'} and self.headers.get('Origin', 'http://' + host) == 'http://' + host

    def do_GET(self):
        if not self.local():
            return self.respond({'error': 'Accès local uniquement'}, 403)
        path = urllib.parse.urlparse(self.path).path
        if path == '/conversation':
            return self.respond((ROOT / 'conversation.html').read_bytes(), content_type='text/html; charset=utf-8')
        if re.fullmatch(r'/api/conversation/[a-f0-9]{32}', path):
            try:
                return self.respond(task_bridge.remote('/api/chat/sessions/' + path.rsplit('/', 1)[1]))
            except Exception as error:
                return self.respond({'error': str(error)}, 502)
        if path == '/execution':
            return self.respond((ROOT / 'execution.html').read_bytes(), content_type='text/html; charset=utf-8')
        if path in {'/api/executions', '/api/execution-goals', '/api/noteplan-tasks'}:
            try:
                if path == '/api/executions':
                    data = {'jobs': task_bridge.jobs()}
                elif path == '/api/execution-goals':
                    data = {'goals': task_bridge.goals()}
                else:
                    query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('q', [''])[0]
                    data = task_bridge.notes(query[:200])
                return self.respond(data)
            except (ValueError, OSError) as error:
                return self.respond({'error': str(error)}, 503)
        if path == '/unification':
            doc = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('doc', [''])[0]
            body, status = render_unification(doc)
            return self.respond(body, status, 'text/html; charset=utf-8')
        if path == '/api/state':
            return self.respond(snapshot())
        if path == '/validate-path':
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            raw = q.get('path', [''])[0]; target = Path(raw).expanduser()
            is_url = urllib.parse.urlparse(raw).scheme in {'https', 'http'}
            ok = (is_url or target.exists()) if q.get('kind') == ['url-or-file'] else target.is_dir()
            return self.respond({'ok': ok, 'path': raw, 'reason': 'ok' if ok else 'Chemin introuvable'})
        if path in {'/station.html', '/control.html'}:
            return self.respond((ROOT / path[1:]).read_bytes(), content_type='text/html; charset=utf-8')
        if path in {'/', '/index.html'}:
            return self.respond((ROOT / 'index.html').read_bytes(), content_type='text/html; charset=utf-8')
        # Only the existing prompt documents are exposed, never a filesystem tree.
        allowed = {'/Prompt-Master-Latest.html', '/latest.md', '/CTxKNL_v0.7.md', '/CTxKNL-launcher-prompt.txt', '/Prompt-Master.html', '/prompt.md'}
        if path in allowed:
            target = STATION / path[1:]
            if target.is_file():
                body = target.read_bytes()
                if path.endswith('.html'):
                    body = body.replace(b'href="AI-Station.html"', b'href="/" target="_top"')
                return self.respond(body, content_type='text/html; charset=utf-8' if path.endswith('.html') else 'text/plain; charset=utf-8')
        return self.respond({'error': 'Introuvable'}, 404)

    def do_POST(self):
        if not self.local():
            return self.respond({'error': 'Accès local uniquement'}, 403)
        if self.path in {'/api/conversation/open', '/api/conversation/send'}:
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size < 32000 or 'application/json' not in self.headers.get('Content-Type', ''):
                    raise ValueError('Requête JSON invalide')
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict): raise ValueError('Objet JSON requis')
                if self.path.endswith('/open'):
                    result = task_bridge.remote('/api/chat/sessions', {'goal_id': 'station-tasks', 'agent_id': 'codex', 'mode': 'resume_latest', 'context_kind': 'goal'})
                else:
                    sid, text, tid = data.get('session_id'), data.get('message'), data.get('client_turn_id')
                    if not isinstance(sid, str) or not re.fullmatch(r'[a-f0-9]{32}', sid): raise ValueError('Session invalide')
                    if not isinstance(text, str) or not text.strip() or len(text) > 6000: raise ValueError('Message invalide')
                    if not isinstance(tid, str) or not re.fullmatch(r'[a-f0-9-]{36}', tid): raise ValueError('Identifiant invalide')
                    result = task_bridge.remote('/api/chat/sessions/' + sid + '/turns', {'message': '[Préférence de langue : réponds en français, sauf si mon message demande explicitement une autre langue.]\n\n' + text, 'client_turn_id': tid})
                return self.respond(result)
            except Exception as error:
                return self.respond({'error': str(error)}, 400)
        if self.path in {'/api/executions/preview', '/api/executions/apply', '/api/executions/validate'}:
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size < 32000 or 'application/json' not in self.headers.get('Content-Type', ''):
                    raise ValueError('Requête JSON invalide')
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict): raise ValueError('Objet JSON requis')
                if self.path.endswith('/validate'):
                    result = task_bridge.validate(data.get('id'), data.get('note'))
                else:
                    result = task_bridge.preview(data) if self.path.endswith('/preview') else task_bridge.apply(data.get('id'))
                return self.respond(result)
            except Exception as error:
                return self.respond({'error': str(error)}, 400)
        if self.path == '/llm-launch':
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 64000:
                    raise ValueError('Requête trop volumineuse ou vide')
            except ValueError as error:
                return self.respond({'error': str(error)}, 400)
            return self.handle_llm_launch()
        if self.path == '/api/legacy-action':
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size < 8000: raise ValueError('Requête invalide')
                data = json.loads(self.rfile.read(size))
                path = data.get('path', '')
                if path.startswith('/launch/'):
                    name = path.split('/')[-1]
                    if name == 'agent-queue' or name not in LAUNCHERS: raise ValueError('Lanceur inconnu')
                    target = STATION / 'launchers' / LAUNCHERS[name]
                elif path == '/open/comfy-output':
                    target = Path('/Users/JOB/#DEV/02-apps/ComfyUI-output')
                elif path == '/open-path':
                    raw = urllib.parse.parse_qs(data.get('query','').lstrip('?')).get('path',[''])[0]
                    if not raw.startswith(('/', '~/')): raise ValueError('Chemin absolu requis')
                    target = Path(raw).expanduser()
                else: raise ValueError('Action inconnue')
                if not target.exists(): raise ValueError('Introuvable : ' + str(target))
                subprocess.run(['/usr/bin/open', str(target)], check=True, timeout=10)
                return self.respond({'ok': True, 'message': 'Ouverture demandée : ' + target.name})
            except (ValueError, AttributeError, OSError, subprocess.SubprocessError) as error:
                return self.respond({'error': str(error)},400)
        if self.path != '/api/launch':
            return self.respond({'error': 'Introuvable'}, 404)
        try:
            size = int(self.headers.get('Content-Length', 0))
            if not 0 < size < 500 or 'application/json' not in self.headers.get('Content-Type', ''):
                raise ValueError('JSON invalide')
            data = json.loads(self.rfile.read(size))
            key = data.get('tool') if isinstance(data, dict) else None
            if key == 'comfyui':
                script = STATION / 'launchers/comfyui.command'
            elif key == 'outputs':
                target = Path('/Users/JOB/#DEV/02-apps/ComfyUI-output')
                if not target.is_dir():
                    raise ValueError('Dossier de sorties absent')
                subprocess.run(['/usr/bin/open', str(target)], check=True, timeout=10)
                return self.respond({'ok': True, 'message': 'Dossier demandé dans Finder.'})
            else:
                content = command_for(key)
                folder = ROOT / 'launchers'
                folder.mkdir(exist_ok=True)
                script = folder / f'{key}.command'
                script.write_text(content)
                script.chmod(0o700)
            subprocess.run(['/usr/bin/open', str(script)], check=True, timeout=10)
            self.respond({'ok': True, 'message': 'Ouverture demandée dans Terminal. Le lancement ne prouve pas une exécution terminée.'})
        except (ValueError, OSError, subprocess.SubprocessError) as error:
            self.respond({'ok': False, 'error': str(error)}, 400)

if __name__ == '__main__':
    task_bridge.start()
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
