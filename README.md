# Tribal Match

Tribal Match is a local full-stack app with:

- `frontend/` for the Next.js web app
- `backend/` for the FastAPI API
- `docker-compose.yml` for the local Postgres database

## Fastest Local Run

Use this path if you just want the app running with minimal setup.

### Prerequisites

- Docker Desktop
- Node.js 20+
- Python 3.10+

### 1. Start Postgres

From the repo root:

```bash
docker compose up -d postgres
```

The database will be available at `localhost:5433`.

### 2. Start the backend

Open a new terminal:

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Notes:

- Use a fresh `.venv`. Do not rely on the checked-in `backend/myenv` folder.
- In development, database migrations run automatically on backend startup.
- The API will be available at `http://127.0.0.1:8000`.
- Swagger docs will be available at `http://127.0.0.1:8000/docs`.

If you use PowerShell instead of Git Bash, activate the virtual environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Start the frontend

Open another terminal:

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

The web app will be available at `http://localhost:3000`.

## Env Defaults

The local setup expects:

- frontend API base URL: `http://localhost:8000/api/v1`
- Postgres URL: `postgresql+psycopg://postgres:newpassword@localhost:5433/tribal_match`

These defaults already match `docker-compose.yml` and the example env files.

## Quick Stop

To stop the database:

```bash
docker compose down
```

To stop the app servers, press `Ctrl+C` in the frontend and backend terminals.
