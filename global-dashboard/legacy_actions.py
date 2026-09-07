from pathlib import Path
import json, shlex, subprocess, time
ROOT=Path(__file__).resolve().parent
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
    "cursor",
    "zcode",
}
ALLOWED_MODELS = {
    "qwen3-coder-next:latest",
    "qwen3-coder:latest",
    "qwen3-coder:30b",
    "devstral-small-2:24b",
    "llama3.2:latest",
    "qwen3:30b",
    "qwen3-embedding:latest",
    "qwen2.5-coder:32b",
    "qwen2.5-coder:14b",
    "dolphin-mistral:latest",
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
class LaunchMixin:
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
                "cursor": "cd \"$TARGET_PATH\"\nprintf '%s\\n' \"$PROMPT\" > .ai-station-prompt.md\nopen -a \"Cursor\" \"$TARGET_PATH\"",
                "zcode": "cd \"$TARGET_PATH\"\nprintf '%s\\n' \"$PROMPT\" > .ai-station-prompt.md\nopen -a \"ZCode\" \"$TARGET_PATH\"",
            }
            return f"""#!/usr/bin/env bash
    set -euo pipefail
    
    TARGET_PATH={shlex.quote(target)}
    PROMPT={shlex.quote(prompt)}
    
    {commands[cli]}
    """
