#!/bin/sh
set -e

# Warten bis DB erreichbar ist
echo "Waiting for database..."
until pg_isready -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  sleep 2
done

# Migrationen ausführen
echo "Running Alembic migrations..."
alembic upgrade head

# Admin seeden (nur wenn nicht vorhanden)
echo "Seeding admin user..."
python -m scripts.seed_admin || true

# Danach Backend starten
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
