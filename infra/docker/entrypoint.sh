#!/usr/bin/env bash
set -euo pipefail

green()  { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }
red()    { printf "\033[31m%s\033[0m\n" "$*"; }

# ====== ENV with defaults ======
: "${SERVER_HOST:=0.0.0.0}"
: "${SERVER_PORT:=8004}"

: "${POSTGRES_HOST:=postgres}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_DB:=ai_screening}"
: "${POSTGRES_USER:=admin}"
: "${POSTGRES_PASSWORD:=admin.admin}"

: "${PG_SUPERUSER:=postgres}"
: "${PG_SUPERPASS:=postgres.pass}"

: "${REDIS_URL:=redis://redis-stack:6379/0}"
: "${RUN_MIGRATIONS:=false}"

# ====== WAIT FOR POSTGRES (pakai superuser agar tidak gagal kalau role admin belum ada) ======
yellow "Waiting for Postgres (${POSTGRES_HOST}:${POSTGRES_PORT}) as ${PG_SUPERUSER} ..."
export PGPASSWORD="${PG_SUPERPASS}"
until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${PG_SUPERUSER}" -d postgres >/dev/null 2>&1; do
  sleep 1
done
green "Postgres is ready."

# ====== IDP: create role admin + DB ai_screening kalau belum ada (AMAN di-run berulang) ======
yellow "Ensuring role '${POSTGRES_USER}' and database '${POSTGRES_DB}' exist..."
psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${PG_SUPERUSER}" -d postgres <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${POSTGRES_USER}') THEN
    CREATE ROLE ${POSTGRES_USER} WITH LOGIN PASSWORD '${POSTGRES_PASSWORD}';
  END IF;
END
\$\$;

DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}') THEN
    PERFORM dblink_exec('dbname=postgres user=${PG_SUPERUSER} password=${PG_SUPERPASS}',
                        'CREATE DATABASE ${POSTGRES_DB}');
  END IF;
END
\$\$;
SQL

# Pastikan extension dblink ada untuk block di atas (pasang jika belum)
psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${PG_SUPERUSER}" -d postgres -v ON_ERROR_STOP=1 -c "CREATE EXTENSION IF NOT EXISTS dblink;" >/dev/null 2>&1 || true

# Set owner DB ke admin (idempotent)
psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${PG_SUPERUSER}" -d postgres -v ON_ERROR_STOP=1 \
  -c "ALTER DATABASE ${POSTGRES_DB} OWNER TO ${POSTGRES_USER};" >/dev/null 2>&1 || true
green "Role/DB ensured."

yellow "Waiting a moment for Redis URL: ${REDIS_URL}"
sleep 1

if [ "${RUN_MIGRATIONS}" = "true" ] && command -v alembic >/dev/null 2>&1; then
  yellow "Running Alembic migrations..."
  export DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
  alembic upgrade head || { red "Alembic migration failed"; exit 1; }
  green "Migrations complete."
fi

yellow "Starting Uvicorn on ${SERVER_HOST}:${SERVER_PORT} ..."
export DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
exec uvicorn app.main:app --host "${SERVER_HOST}" --port "${SERVER_PORT}" --reload
