# Ghosty — Web Client

Minimal React + TypeScript chat client for the Ghosty messenger.

## Prerequisites

- Node.js 18+
- The Ghosty backend running on `localhost:8000`

## Setup & run

```bash
cd clients/web
npm install
npm run dev
```

The dev server starts at **http://localhost:5173**.

## Usage

1. Start the backend (`uvicorn server.main:app --reload` from the repo root).
2. Open the app in the browser — it connects automatically with token `anton`.
3. Enter a **recipient_id** and a message, then press **Send** or **Enter**.

## ⚠️ WebSocket authentication note

Browsers cannot set arbitrary HTTP headers during a WebSocket handshake. The
client passes the token as a **query parameter** (`?token=anton`).

The backend currently reads the token from `ws.headers.get("token")`. To make
the web client authenticate correctly, update the relevant line in
`server/main.py`:

```python
# Before
token = ws.headers.get("token")

# After (one line)
token = ws.headers.get("token") or ws.query_params.get("token")
```

The desktop client (coming under `clients/desktop/`) will connect via a runtime
that supports custom HTTP headers and won't need this change.

## Project structure

```
clients/web/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── src/
    ├── main.tsx              # entry point
    ├── App.tsx               # single chat screen
    ├── App.css               # all styles
    ├── services/
    │   └── websocket.ts      # WebSocketService singleton
    └── types/
        └── events.ts         # typed event interfaces
```
