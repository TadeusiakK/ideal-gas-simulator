# ideal-gas-simulator

A real-time 2D ideal gas simulation in which the Maxwell-Boltzmann speed
distribution emerges from elastic collisions between particles.


## Stack

| Layer | Technology |
|---|---|
| Engine | Python 3.12, standard library only |
| API | FastAPI + Uvicorn (WebSocket + OpenAPI) |
| Tests | pytest |
| Frontend | Vue 3 (Composition API) + Vite + TypeScript |
| Frontend tooling | ESLint + oxlint + Prettier |

## Repository layout

```
ideal-gas-simulator/
├── backend/
│   ├── gas/              pure simulation engine - standard library only
│   ├── api/              FastAPI layer: schemas, WebSocket handler, app entry
│   ├── tests/            pytest suite for engine and API
│   └── run.py            uvicorn entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/   canvas renderers and control panel
│   │   ├── composables/  WebSocket state handling
│   │   ├── types.ts      message contract shared with the backend
│   │   ├── App.vue
│   │   └── main.ts
│   ├── public/           static assets
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts    dev server and build; `/api` and `/ws` proxy to add
│   └── tsconfig*.json    TypeScript project references
└── requirements.txt      Python dependencies of the API
```

Inside `frontend/`, `src/components/`, `src/composables/` and `src/types.ts` are
the parts this project adds; the remaining Vue files are baseline configuration.

**Isolation rule:** `gas/` imports nothing from FastAPI, Vue or pygame. The
engine exposes only `Engine.step(dt)` and `Engine.snapshot()`; the API layer
serialises a snapshot and the frontend renders one.

## Requirements

The API dependencies are listed in `requirements.txt` and must be installed
before running anything:

```powershell
python -m venv env
.\env\Scripts\python.exe -m pip install -r requirements.txt
```