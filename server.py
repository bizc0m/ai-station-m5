#!/usr/bin/env python3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import cgi
import json
import os
import shlex
import subprocess
import tempfile
import time
import urllib.parse

ROOT = Path(__file__).resolve().parent
COMFY_OUTPUT = Path("/Users/JOB/#DEV/02-apps/ComfyUI-output")
QUEUE_CLI = Path("/Users/JOB/#DEV/_Agents/task-queue/scripts/agent-queue")
QUEUE_UPLOADS = Path("/Users/JOB/#DEV/_Agents/task-queue/tmp/uploads")
LAUNCHERS = {
    "agent-queue": "agent-queue.command",
    "aider": "aider.command",
    "aider-fast": "aider-fast.command",
    "claude": "claude.command",
    "claude-caveman": "claude-caveman.command",
    "cline": "cline.command",
    "codeman": "codeman.command",
    "codex": "codex.command",
    "comfyui": "comfyui.command",
    "cursor": "cursor.command",
    "goose": "goose.command",
    "hermes": "hermes.command",
    "hermes-fast": "hermes-fast.command",
    "hermes-lite": "hermes-lite.command",
    "hermes-qwen3-coder": "hermes-qwen3-coder.command",
    "opencode": "opencode.command",
    "openhands": "openhands.command",
    "ollama-menu": "ollama-menu.command",
    "prompt-master": "prompt-master.command",
    "zcode": "zcode.command",
}
ALLOWED_LLMS = {
    "ollama",
    "hermes",
    "aider",
    "codex",
    "opencode",
    "claude",
}
ALLOWED_MODELS = {
    "qwen3-coder:30b",
    "devstral-small-2:24b",
    "qwen2.5-coder:32b",
    "qwen2.5-coder:14b",
    "qwen3:32b",
    "qwen3:8b",
    "deepseek-r1:32b",
    "gemma3:27b",
}
ALLOWED_MODES = {"chat", "dev", "app", "dash"}
ALLOWED_PROMPT_SOURCES = {
    "latest.md",
    "CTxKNL-launcher-prompt.txt",
    "CTxKNL_v0.7.md",
    "https://bizc0m.github.io/prompt-master/latest.md",
}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def guess_type(self, path):
        content_type = super().guess_type(path)
        if path.endswith((".txt", ".md", ".html", ".css", ".js")) and "charset=" not in content_type:
            return f"{content_type}; charset=utf-8"
        return content_type

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/validate-path":
            query = urllib.parse.parse_qs(parsed.query)
            raw_path = query.get("path", [""])[0].strip()
            kind = query.get("kind", ["dir"])[0]
            parsed_target = urllib.parse.urlparse(raw_path)
            candidate = Path(raw_path).expanduser()
            is_url = parsed_target.scheme in {"http", "https"} and bool(parsed_target.netloc)
            is_local = raw_path.startswith(("/", "~/")) and candidate.exists()
            if kind == "url-or-file":
                ok = is_url or is_local
                reason = "ok" if ok else "url ou fichier local introuvable"
            else:
                ok = raw_path.startswith(("/", "~/")) and candidate.is_dir()
                reason = "ok" if ok else "dossier introuvable"
            payload = json.dumps({
                "ok": ok,
                "path": raw_path,
                "reason": reason,
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if parsed.path == "/open/comfy-output":
            subprocess.Popen(["open", str(COMFY_OUTPUT)])
            self.send_response(303)
            self.send_header("Location", "/AI-Station.html")
            self.end_headers()
            return
        if parsed.path == "/open-path":
            query = urllib.parse.parse_qs(parsed.query)
            raw_path = query.get("path", [""])[0].strip()
            target = Path(raw_path).expanduser()
            if not raw_path.startswith(("/", "~/")) or not target.exists():
                self.send_error(404, "Path not found")
                return
            subprocess.Popen(["open", str(target)])
            self.send_response(303)
            self.send_header("Location", "/AI-Station.html")
            self.end_headers()
            return
        if parsed.path.startswith("/launch/"):
            name = parsed.path.removeprefix("/launch/")
            script = LAUNCHERS.get(name)
            if not script:
                self.send_error(404, "Unknown launcher")
                return
            target = ROOT / "launchers" / script
            subprocess.Popen(["open", str(target)])
            self.send_response(303)
            self.send_header("Location", "/AI-Station.html")
            self.end_headers()
            return
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/queue/add":
            self.handle_queue_add()
            return
        if parsed.path == "/llm-launch":
            self.handle_llm_launch()
            return
        self.send_error(404, "Unknown POST route")

    def handle_llm_launch(self):
        if "application/json" not in self.headers.get("Content-Type", ""):
            self.send_json({"ok": False, "error": "application/json required"}, status=400)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception as exc:
            self.send_json({"ok": False, "error": f"json invalide: {exc}"}, status=400)
            return

        cli = str(payload.get("cli", "")).strip()
        model = str(payload.get("model", "")).strip()
        mode = str(payload.get("mode", "")).strip()
        prompt_source = str(payload.get("promptSource", "")).strip()
        request = str(payload.get("request", "")).strip()
        target_raw = str(payload.get("targetPath", "")).strip() or "/Users/JOB/#DEV"
        target = Path(target_raw).expanduser()

        if cli not in ALLOWED_LLMS or model not in ALLOWED_MODELS or mode not in ALLOWED_MODES:
            self.send_json({"ok": False, "error": "cli, modèle ou mode non autorisé"}, status=400)
            return
        if prompt_source not in ALLOWED_PROMPT_SOURCES:
            self.send_json({"ok": False, "error": "source prompt non autorisée"}, status=400)
            return
        if not request:
            self.send_json({"ok": False, "error": "requête vide"}, status=400)
            return
        try:
            resolved = target.resolve()
        except FileNotFoundError:
            self.send_json({"ok": False, "error": "chemin introuvable"}, status=400)
            return
        if not resolved.is_dir() or not str(resolved).startswith("/Users/JOB/"):
            self.send_json({"ok": False, "error": "chemin projet non autorisé"}, status=400)
            return

        prompt = self.build_llm_prompt(mode, prompt_source, str(resolved), request)
        script = self.build_llm_script(cli, model, str(resolved), prompt)
        tmp_dir = ROOT / "tmp" / "llm-launch"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        script_path = tmp_dir / f"llm-{int(time.time())}.command"
        script_path.write_text(script, encoding="utf-8")
        script_path.chmod(0o700)
        subprocess.Popen(["open", str(script_path)])
        self.send_json({"ok": True, "script": str(script_path)})

    def build_llm_prompt(self, mode, prompt_source, target, request):
        modes = {
            "chat": ("Chat", "[BASE] [MODUL]", "Réponse directe, pas de protocole DEV si demande simple."),
            "dev": ("Dev", "[BASE] [MODUL] [PTHCOD] [GIT?] [SOURCE?] [DELIV?]", "Code, repo, tests, Git, preuves."),
            "app": ("App", "[BASE] [MODUL] [PTHCOD] [APP] [GIT?] [DELIV?]", "App macOS, runtime, fenêtres, UX native."),
            "dash": ("Dashboard", "[BASE] [MODUL] [PTHCOD] [DASHUX] [GIT?] [DELIV?]", "HTML, UI, responsive, rendu vérifié."),
        }
        label, modules, hint = modes[mode]
        return f"""Charge CTxKNL avant de répondre.

Source :
{prompt_source}

Mode : {label}
Modules : {modules}
Path : {target}

Règles :
- {hint}
- Compter chaque prompt utilisateur et afficher le footer compteur.
- Ne pas push sans demande explicite.
- Répondre court : ACT / RES / NEXT.

Demande :
{request}
"""

    def build_llm_script(self, cli, model, target, prompt):
        quoted_model = shlex.quote(model)
        quoted_ollama_model = shlex.quote(f"ollama/{model}")
        commands = {
            "ollama": f"ollama run {quoted_model} \"$PROMPT\"",
            "hermes": f"hermes -m {quoted_model} -z \"$PROMPT\"",
            "aider": f"cd \"$TARGET_PATH\"\naider --model {quoted_ollama_model} --message \"$PROMPT\"",
            "codex": "cd \"$TARGET_PATH\"\ncodex \"$PROMPT\"",
            "opencode": "cd \"$TARGET_PATH\"\nopencode \"$PROMPT\"",
            "claude": "cd \"$TARGET_PATH\"\nclaude \"$PROMPT\"",
        }
        return f"""#!/usr/bin/env bash
set -euo pipefail

TARGET_PATH={shlex.quote(target)}
PROMPT={shlex.quote(prompt)}

{commands[cli]}
"""

    def handle_queue_add(self):
        ctype, pdict = cgi.parse_header(self.headers.get("Content-Type", ""))
        if ctype != "multipart/form-data":
            self.send_error(400, "multipart/form-data required")
            return
        pdict["boundary"] = bytes(pdict["boundary"], "utf-8")
        pdict["CONTENT-LENGTH"] = int(self.headers.get("Content-Length", "0"))
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": self.headers.get("Content-Type", ""),
        })
        request = (form.getfirst("request") or "").strip()
        agent = (form.getfirst("agent") or "").strip()
        priority = (form.getfirst("priority") or "3").strip()
        if not request:
            self.send_json({"ok": False, "error": "requête vide"}, status=400)
            return

        QUEUE_UPLOADS.mkdir(parents=True, exist_ok=True)
        upload_dir = Path(tempfile.mkdtemp(prefix="queue-", dir=str(QUEUE_UPLOADS)))
        attachments = []
        documents = form["documents"] if "documents" in form else []
        if not isinstance(documents, list):
            documents = [documents]
        for item in documents:
            if not getattr(item, "filename", ""):
                continue
            filename = Path(item.filename).name
            target = upload_dir / filename
            with target.open("wb") as handle:
                handle.write(item.file.read())
            attachments.extend(["--attach", str(target)])

        title = request.splitlines()[0][:120]
        cmd = [
            str(QUEUE_CLI),
            "add",
            title,
            "--priority",
            priority,
            "--notes",
            request,
        ]
        if agent:
            cmd.extend(["--agent", agent])
        cmd.extend(attachments)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            self.send_json({"ok": False, "error": result.stderr.strip() or result.stdout.strip()}, status=500)
            return
        task_id = result.stdout.strip().splitlines()[-1]
        self.send_json({"ok": True, "task_id": task_id})

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/open/comfy-output":
            self.send_response(204)
            self.end_headers()
            return
        if parsed.path == "/validate-path":
            self.send_response(204)
            self.end_headers()
            return
        if parsed.path == "/open-path":
            self.send_response(204)
            self.end_headers()
            return
        if parsed.path.startswith("/launch/"):
            name = parsed.path.removeprefix("/launch/")
            if name not in LAUNCHERS:
                self.send_error(404, "Unknown launcher")
                return
            self.send_response(204)
            self.end_headers()
            return
        return super().do_HEAD()


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8765), Handler).serve_forever()
