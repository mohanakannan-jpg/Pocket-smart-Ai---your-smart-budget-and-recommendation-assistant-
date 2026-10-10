# PocketSmart AI

PocketSmart AI is a calculation-first budgeting assistant for home interiors, parties/events, and jewelry purchases. It keeps budgets transparent, lets authenticated users save private plans, and provides budget-aware guidance without pretending illustrative data is live commerce data.

## Features

- Three editable planners: Home Interior, Party & Event, and Jewelry.
- Server-side integer-minor-unit arithmetic: category totals, verified versus illustrative spend, remaining amount, utilization, over-budget warnings, and unpriced-item handling.
- Registration, login, signed expiring bearer sessions, scrypt password hashes, and ownership-enforced saved plans.
- Budget-aware illustrative product suggestions filtered to the plan's remaining budget; catalog entries are explicitly labelled as non-live data.
- Optional Gemini configuration point. Core calculations and recommendation fallback work without any AI key.
- Responsive React interface with form validation, empty states, errors, and save/reopen workflow.

## Architecture

```
src/                 React + TypeScript + Vite frontend
backend/app/         FastAPI API, SQLAlchemy models, services
backend/tests/       Pytest calculation tests
```

SQLite is initialized automatically at backend startup (`backend/pocketsmart.db`). Monetary amounts are persisted/calculated as integer minor units on the API boundary. Planner payloads are JSON to allow planner-specific fields while plans remain ownership-protected.

## Prerequisites

- Node.js 20+
- Python 3.11+ (3.14 used during development; package availability can vary by platform)

## Run locally (Windows PowerShell)

```powershell
Copy-Item .env.example .env
npm install
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

In one PowerShell window, start the API from the `backend` directory so SQLite stays there:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

In another PowerShell window at the repository root:

```powershell
npm run dev
```

Open `http://localhost:5173`. API documentation is available at `http://localhost:8000/docs`.

## Environment

Copy `.env.example` to `.env` and set a long random `JWT_SECRET` before deploying. `GEMINI_API_KEY` and `GEMINI_MODEL` are reserved exclusively for server-side Gemini enhancement; do not expose them as `VITE_*` variables. If configured, the API asks Gemini for one tightly bounded JSON explanation, validates it, and falls back cleanly when it fails.

`FRONTEND_ORIGIN` controls the development CORS origin. For production, use HTTPS, a managed database, secure HTTP-only cookie/session strategy or an equivalent hardened token setup, a strong rotated secret, rate limiting, and a narrowly scoped CORS configuration.

## Tests and build

```powershell
npm run build
npm test
cd backend
pytest -q
```

## Product and AI data policy

The bundled catalog is illustrative only. It has no product URLs, live availability, or merchant claims. A real provider should implement the interface in `backend/app/products.py` with an authorized API/feed and source timestamps. Unknown prices are never counted as zero.

AI is additive, never authoritative: arithmetic, authorization, and product truth remain server-controlled. When AI is unavailable, PocketSmart returns deterministic, transparent suggestions.

## Limitations

- No live retailer or vendor integration is configured.
- Outfit uploads and image analysis are intentionally not included in this local vertical slice; no user image is collected or exposed.
- Gemini requires an API key, internet access, quota, and a supported model; its explanatory response is optional and can fail over to deterministic guidance.

## Review and GitHub

```powershell
git status
git diff --check
git add README.md .env.example .gitignore package.json src backend
git commit -m "Build PocketSmart AI budgeting application"
git push origin <your-branch>
```

Do not commit `.env`, `backend/pocketsmart.db`, virtual environments, or build output.
