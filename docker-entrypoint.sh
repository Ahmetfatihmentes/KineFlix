#!/usr/bin/env sh
set -e

# Kalıcı SQLite dizini (docker-compose volume ile eşlenir)
mkdir -p /app/data

if [ -z "${DATABASE_URL:-}" ]; then
  export DATABASE_URL="sqlite:////app/data/kineflix.db"
fi

echo "Applying database migrations (alembic upgrade head)..."
if python - <<'PY'
import os, sqlite3, sys
url = os.getenv("DATABASE_URL", "")
if not url.startswith("sqlite:///"):
    sys.exit(2)
path = url.replace("sqlite:///", "", 1)
if path.startswith("./"):
    path = "/app/" + path[2:]
if not os.path.exists(path):
    sys.exit(1)
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
exists = cur.fetchone() is not None
conn.close()
sys.exit(0 if exists else 1)
PY
then
  echo "Existing SQLite tables detected. Stamping alembic head and continuing..."
  alembic stamp head
else
  alembic upgrade head
fi

echo "Starting application..."
exec "$@"
