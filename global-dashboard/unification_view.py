from pathlib import Path
from html import escape
from urllib.parse import quote

REPO = Path('/Users/JOB/Documents/Codex/2026-09-05/qu/outputs/Unification')

def render(document=''):
    files = [REPO / 'INDEX.md', REPO / 'INTEGRATION.md']
    files += sorted((REPO / 'chats').glob('*.md')) + sorted((REPO / 'projets').glob('*.md'))
    allowed = {p.relative_to(REPO).as_posix(): p for p in files if p.is_file() and not p.is_symlink()}
    if document and document not in allowed:
        return b'Fiche introuvable', 404
    links = ''.join('<li><a href="/unification?doc=' + quote(name) + '">' + escape(name) + '</a></li>' for name in allowed)
    content = '<pre>' + escape(allowed[document].read_text()) + '</pre>' if document else '<p>Choisis une fiche. Les résultats déclarés restent distincts des résultats vérifiés.</p>'
    html = '<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Unification</title><style>body{font:14px system-ui;margin:24px;background:#f5f4ef;color:#202820}a{color:#275d45}li{margin:10px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:20px;border:1px solid #dce1d8;border-radius:10px}aside{overflow-wrap:anywhere}</style><h1>Unification</h1><p>Fiches du clone local, en lecture seule. Les nouvelles publications GitHub apparaissent après actualisation du clone.</p><a href="https://github.com/bizc0m/Unification" target="_blank" rel="noopener">Dépôt privé GitHub</a><aside><ul>' + links + '</ul></aside>' + content + '</html>'
    return html.encode(), 200
