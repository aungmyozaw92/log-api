## FastAPI Auth + Logs — Setup Guide

### 1) Clone the repo
```bash
git clone <your-repo-url> fastapi-auth
cd fastapi-auth
```

### 2) Create and activate a virtual environment (Python 3.9+)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Configure environment
Create a `.env` file in the project root (or set env vars another way):
```env
PROJECT_NAME=Log Management Rest API
API_V1_STR=/api/v1
SECRET_KEY=replace-with-a-random-long-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/dbname
DEBUG=true
```

### 5) Initialize the database
Tables are created automatically on app startup. You can start the app once to ensure tables exist:
```bash
python run.py
```

### 6) (Optional) Seed data
Create an admin user and generate sample logs:
```bash
python -m app.seed --admin-password 'Admin@12345' --logs 100
```

### 7) Start the API server
Either of the following works (they use the same app):
```bash
python run.py
# or
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 8) Explore the API
- Open docs: http://localhost:8000/docs
- Health check: `GET /health`
- Auth routes (prefix `${API_V1_STR}/auth`):
  - `POST /register` → body: `{ username, password, name, email }`
  - `POST /login` (OAuth2 form) → returns token and user
  - `GET /profile` (Bearer token)
- Logs routes (prefix `${API_V1_STR}/logs`):
  - `POST /` create log
  - `GET /` list with filters `start,end,severity,source,limit,offset`
  - `GET /{id}` fetch one
  - `PATCH /{id}` update
  - `DELETE /{id}` delete
  - `GET /aggregate/by/{severity|source}` aggregated counts

### CSV Export (background job)
Exports are processed via Redis and RQ.

1) Start Redis locally (default `redis://localhost:6379/0`).

2) Start an RQ worker (macOS-safe non-forking):
```bash
source venv/bin/activate
python run_worker.py
```

Optionally set the output directory for CSV files (defaults to `/tmp`):
```bash
EXPORT_DIR="$(pwd)/exports" python run_worker.py
```

3) Enqueue an export via API:
```http
POST ${API_V1_STR}/logs/export?start=2024-01-01T00:00:00&end=2024-12-31T23:59:59&severity=INFO&source=app
```
Response contains `{ job_id }`.

4) Check status/download:
- Status: `GET ${API_V1_STR}/logs/export/{job_id}`
- Download: `GET ${API_V1_STR}/logs/export/{job_id}/download`

### Response format
All responses use a unified envelope:
```json
{ "success": true|false, "message": "text", "data": { ... } }
```

Validation errors (422):
```json
{ "success": false, "message": "Validation error", "data": { "errors": [ ... ] } }
```

HTTP errors (401/403/404/...):
```json
{ "success": false, "message": "reason", "data": null }
```

### Admin credentials (seeded)
- username: `admin`
- password: as provided to the seeder (default `Admin@12345`)

### Common commands
```bash
# Activate venv
source venv/bin/activate

# Run server
python run.py

# Seed data
python -m app.seed --logs 200
```

### Testing
Install test dependencies and run the suite:
```bash
source venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```
What is covered:
- Health endpoint
- Logs CRUD and aggregation
- Auth: register, login (OAuth2 form), profile
- Users CRUD
- Export enqueue (Redis queue is mocked)


