"""Web adaptor defaults."""

# Local HTTP server defaults.
DEFAULT_WEB_HOST = "127.0.0.1"
DEFAULT_WEB_PORT = 8765

# Bundled web entry file.
DEFAULT_INDEX_FILE = "index.html"

# Project-local Codex preset storage.
DEFAULT_CODEX_PRESETS_PATH = "data/codex_presets.json"

# Keep API switching on one stable provider to preserve Codex history.
DEFAULT_CODEX_PROVIDER_ID = "ai_api_tester"

# Codex runtime defaults for the connection page.
DEFAULT_CODEX_APPROVAL_POLICY = "on-request"
DEFAULT_CODEX_SANDBOX_MODE = "workspace-write"
CODEX_APPROVAL_POLICY_OPTIONS = ("never", "on-request")
CODEX_SANDBOX_MODE_OPTIONS = ("danger-full-access", "workspace-write")

