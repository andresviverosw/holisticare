#!/usr/bin/env bash
# US-OPS-SCHEMA-001 — apply HolistiCare schema in a fixed order.
#
# Usage (local Compose DB):
#   DATABASE_URL=postgresql://holisticare:holisticare@localhost:5432/holisticare_db ./scripts/migrate.sh
#
# Usage (Render External Database URL):
#   DATABASE_URL='postgresql://...onrender.com/...' ./scripts/migrate.sh
#
# This is the single bootstrap path for empty volumes. Prefer this over
# remembering patch file order by hand. Alembic may supersede this later;
# until then, init.sql + ordered patches ARE the migration set.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA="${ROOT}/infra"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: set DATABASE_URL (postgres connection string)." >&2
  exit 1
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "ERROR: psql is required on PATH." >&2
  exit 1
fi

FILES=(
  "${INFRA}/init.sql"
  "${INFRA}/patch_intake_and_longitudinal.sql"
  "${INFRA}/patch_plan_memory_bank.sql"
)

for f in "${FILES[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "ERROR: missing migration file: $f" >&2
    exit 1
  fi
  echo "==> Applying $(basename "$f")"
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$f"
done

echo "OK: schema bootstrap complete (${#FILES[@]} files)."
