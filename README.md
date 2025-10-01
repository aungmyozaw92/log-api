## FastAPI Log Management API — Setup Guide

### Prerequisites
- Python 3.9+
- Redis (local service or Docker)

### 
1) Clone the repo
```bash
git clone <your-repo-url> log-api
cd log-api
```

### Step-by-step (after cloning)
2) Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3) Install dependencies
```bash
pip install -r requirements.txt
```

4) Create a .env file in the project root
```env
PROJECT_NAME=Log Management Rest API
API_V1_STR=/api/v1
SECRET_KEY=replace-with-a-random-long-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/dbname
DEBUG=true
REDIS_URL=redis://localhost:6379/0
EXPORT_DIR=./exports

```
5) Seed data
```bash
python -m app.seed --admin-password 'Admin@12345' --logs 200
```

6) Start Redis
- macOS (Homebrew): `brew services start redis`
- Docker alternative: `docker run --name redis -p 6379:6379 -d redis:7-alpine`

7) Run the API server (also initializes DB tables)
```bash
python run.py
```

8) Start the background worker for CSV exports (in a second terminal)
```bash
source venv/bin/activate
EXPORT_DIR="$(pwd)/exports" python run_worker.py
```

9) Use the API
- Docs: http://localhost:8000/docs
- Health: `GET /health`
- Auth (prefix `${API_V1_STR}/auth`):
  - `POST /register` { username, password, name, email }
  - `POST /login` (OAuth2 form) → token + user
  - `GET /profile` (requires Bearer token)
- Logs (prefix `${API_V1_STR}/logs`):
  - `POST /` create
  - `GET /` list with filters `start,end,severity,source,limit,offset`
  - `GET /{id}` get one
  - `PATCH /{id}` update
  - `DELETE /{id}` delete
  - `GET /aggregate/by/{severity|source}` aggregate

10) CSV export workflow
```http
POST ${API_V1_STR}/logs/export?start=2024-01-01T00:00:00&end=2024-12-31T23:59:59&severity=INFO&source=app
```
- Check status: `GET ${API_V1_STR}/logs/export/{job_id}`
- Download: `GET ${API_V1_STR}/logs/export/{job_id}/download`

### Testing
Run the test suite:
```bash
python -m pytest -q
```
Coverage: health, logs CRUD + aggregation, auth register/login/profile, users CRUD, export enqueue (queue mocked).


