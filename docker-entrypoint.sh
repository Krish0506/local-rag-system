#!/usr/bin/env sh
set -eu

echo "Waiting for PostgreSQL..."

python - <<'PY'
import sys
import time

import psycopg2

from app.config.settings import settings

deadline = time.time() + 60
last_error = None

while time.time() < deadline:
    try:
        with psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            connect_timeout=3,
        ):
            print("PostgreSQL is ready.")
            break
    except psycopg2.OperationalError as exc:
        last_error = exc
        time.sleep(2)
else:
    print(f"PostgreSQL did not become ready in time: {last_error}", file=sys.stderr)
    sys.exit(1)
PY

python create_tables.py

exec streamlit run app/ui/streamlit_app.py \
    --server.address=0.0.0.0 \
    --server.port=8501 \
    --server.headless=true
