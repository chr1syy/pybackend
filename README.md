# pybackend
Backend with FastAPI and Postgres

# Dev

1. Clone Repo

2. Copy .env.example to your local .env and change settings

2. Create Virtual Environment
```
python -m venv .venv
source .venv/bin/activate
```
3. Install Requirements
```
pip install -r requirements.txt
```

4. Start DB in Folder db with Docker-Compose up
```
docker-compose -f docker-compose.dev.yml up -d
```

5. Init Database
```
alembic upgrade head
```

6. Start Backend locally
```
uvicorn app.main:app --reload
```

7. Running `pytest` automatically Seeds Admin User with Admin Password and runs the Endpoint tests


# Prod

1. Clone Repo

2. Copy .env.example to your local .env and change settings

3. Start Docker Container
```
docker-compose -f docker-compose.prod.yml up --build
```