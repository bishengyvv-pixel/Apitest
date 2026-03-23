## React Web

This directory contains the React frontend for the project.

### Development

1. Start the backend:
   `uv run python main.py web`
2. Start the frontend dev server:
   `npm run dev`

Vite proxies local `/api/*` traffic to `http://127.0.0.1:8765`, so development still goes through the project's Python Web BFF instead of calling the upstream API directly from the browser.

### Build

Run:

```bash
npm run build
```

The build output is written directly to:

`packages/ai_api_tester_web/assets`

That lets `uv run python main.py web` serve the compiled React app directly.
