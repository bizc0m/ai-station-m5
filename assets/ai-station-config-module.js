const STORAGE_KEY = "ai_station_public_config_v1";

const DEFAULT_CONFIG = {
  title: "AI Station",
  repoUrl: "https://github.com/your-user/your-repo",
  localUrl: "http://127.0.0.1:8765/AI-Station.html",
  promptUrl: "https://example.com/prompt.md",
  ollamaUrl: "http://127.0.0.1:11434/api/tags",
  models: [
    "qwen3-coder:30b",
    "devstral-small-2:24b",
    "qwen2.5-coder:32b",
    "qwen3:8b"
  ],
  apps: [
    "Codex",
    "Claude",
    "Cursor",
    "ZCode",
    "OpenCode"
  ]
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function normalizeLines(value) {
  return String(value)
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function readConfig() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? { ...DEFAULT_CONFIG, ...JSON.parse(saved) } : { ...DEFAULT_CONFIG };
  } catch (_) {
    return { ...DEFAULT_CONFIG };
  }
}

function writeConfig(config) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config, null, 2));
}

function buildStandaloneHtml(config) {
  const models = config.models.map((model) => `<li>${escapeHtml(model)}</li>`).join("\n");
  const apps = config.apps.map((app) => `<li>${escapeHtml(app)}</li>`).join("\n");
  return `<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(config.title)}</title>
  <style>
    body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif;background:#fff;color:#111}
    main{width:min(920px,calc(100% - 32px));margin:32px auto}
    h1{font-size:28px;margin:0 0 8px}
    section{border:1px solid #ddd;border-radius:8px;padding:16px;margin:14px 0}
    a{color:#0b6b35} code{background:#f5f5f5;padding:2px 5px;border-radius:4px}
    ul{columns:2;line-height:1.7}
  </style>
</head>
<body>
  <main>
    <h1>${escapeHtml(config.title)}</h1>
    <p>Page publique générée sans chemin utilisateur ni donnée privée par défaut.</p>
    <section>
      <h2>Liens</h2>
      <p>Git : <a href="${escapeHtml(config.repoUrl)}">${escapeHtml(config.repoUrl)}</a></p>
      <p>Station locale : <code>${escapeHtml(config.localUrl)}</code></p>
      <p>Prompt : <a href="${escapeHtml(config.promptUrl)}">${escapeHtml(config.promptUrl)}</a></p>
      <p>Ollama : <code>${escapeHtml(config.ollamaUrl)}</code></p>
    </section>
    <section>
      <h2>Modèles</h2>
      <ul>${models}</ul>
    </section>
    <section>
      <h2>Apps / CLI</h2>
      <ul>${apps}</ul>
    </section>
  </main>
</body>
</html>`;
}

function downloadHtml(filename, html) {
  const blob = new Blob([html], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function initAiStationConfigurator(root = document) {
  const form = root.querySelector("[data-config-form]");
  const output = root.querySelector("[data-config-output]");
  const saveButton = root.querySelector("[data-save-config]");
  const downloadButton = root.querySelector("[data-download-html]");
  const copyButton = root.querySelector("[data-copy-config]");
  if (!form || !output) return;

  const fields = {
    title: form.elements.title,
    repoUrl: form.elements.repoUrl,
    localUrl: form.elements.localUrl,
    promptUrl: form.elements.promptUrl,
    ollamaUrl: form.elements.ollamaUrl,
    models: form.elements.models,
    apps: form.elements.apps
  };

  function configFromForm() {
    return {
      title: fields.title.value.trim() || DEFAULT_CONFIG.title,
      repoUrl: fields.repoUrl.value.trim() || DEFAULT_CONFIG.repoUrl,
      localUrl: fields.localUrl.value.trim() || DEFAULT_CONFIG.localUrl,
      promptUrl: fields.promptUrl.value.trim() || DEFAULT_CONFIG.promptUrl,
      ollamaUrl: fields.ollamaUrl.value.trim() || DEFAULT_CONFIG.ollamaUrl,
      models: normalizeLines(fields.models.value),
      apps: normalizeLines(fields.apps.value)
    };
  }

  function render() {
    const config = configFromForm();
    output.textContent = buildStandaloneHtml(config);
  }

  function load(config) {
    fields.title.value = config.title;
    fields.repoUrl.value = config.repoUrl;
    fields.localUrl.value = config.localUrl;
    fields.promptUrl.value = config.promptUrl;
    fields.ollamaUrl.value = config.ollamaUrl;
    fields.models.value = config.models.join("\n");
    fields.apps.value = config.apps.join("\n");
    render();
  }

  form.addEventListener("input", render);
  saveButton?.addEventListener("click", () => {
    writeConfig(configFromForm());
    saveButton.textContent = "Sauvé";
    setTimeout(() => {
      saveButton.textContent = "Sauver config";
    }, 1200);
  });
  downloadButton?.addEventListener("click", () => {
    const config = configFromForm();
    const filename = `${config.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "ai-station"}.html`;
    downloadHtml(filename, buildStandaloneHtml(config));
  });
  copyButton?.addEventListener("click", async () => {
    await navigator.clipboard.writeText(JSON.stringify(configFromForm(), null, 2));
    copyButton.textContent = "Copié";
    setTimeout(() => {
      copyButton.textContent = "Copier config";
    }, 1200);
  });

  load(readConfig());
}

