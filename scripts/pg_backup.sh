.#!/bin/bash
set -euo pipefail

# ------------------- KONFIGURATION -------------------
DB_NAME="postgres"
DB_USER="postgres"
PGHOST="127.0.0.1"
PGPORT="5432"

BACKUP_USER="nico7634"
BACK_HOST="192.168.20.50"
BACKUP_DIR="/home/nico7634/db_backups"

SSH_KEY="${HOME}/.ssh/id_backup"
RETENTION_DAYS=30

# ------------------- FILNAVNE & TMP -------------------
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
FILENAME="${DB_NAME}-${TIMESTAMP}.sql.gz"
LOCAL_TMP="$(mktemp --tmpdir="${TMPDIR:-/tmp}" "dbbackup-XXXXXX-${FILENAME}")"

# ------------------- CLEANUP -------------------
cleanup() {
  rc=$?
  rm -f "$LOCAL_TMP" || true
  exit $rc
}
trap cleanup EXIT INT TERM

# ------------------- ERROR FUNCTION -------------------
err() { echo "FEJL: $*" >&2; exit 1; }

# ------------------- KOMMANDO-TJEK -------------------
for cmd in pg_dump gzip scp ssh mktemp date find; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    err "Påkrævet kommando mangler: $cmd"
  fi
done

# ------------------- PGPASS ADVARSEL -------------------
if [[ ! -f "${HOME}/.pgpass" ]]; then
  echo "Advarsel: ~/.pgpass findes ikke. Hvis Postgres kræver password, vil pg_dump bede om det." >&2
fi

# ------------------- SIKR FJERNMAPPE -------------------
echo "Sikrer fjern-mappe på ${BACK_HOST}..."
ssh -i "$SSH_KEY" -o BatchMode=yes -o ConnectTimeout=10 \
  "${BACKUP_USER}@${BACK_HOST}" "mkdir -p '${BACKUP_DIR}'" \
  || err "Kunne ikke oprette/få adgang til ${BACK_HOST}:${BACKUP_DIR} (ssh fejl)"

# ------------------- LAV BACKUP -------------------
echo "Starter pg_dump for database '${DB_NAME}' (host: ${PGHOST}:${PGPORT})..."
PGPASSWORD="${PGPASSWORD:-}" \
pg_dump -h "$PGHOST" -p "$PGPORT" -U "$DB_USER" "$DB_NAME" \
  2>/tmp/pg_dump.err | gzip > "$LOCAL_TMP" || {
    echo "pg_dump fejlede. Sidste fejl (kort):" >&2
    tail -n 50 /tmp/pg_dump.err || true
    err "pg_dump mislykkedes"
  }

# ------------------- SEND BACKUP TIL VM -------------------
echo "Overfører backup til ${BACK_HOST}:${BACKUP_DIR}/${FILENAME} ..."
scp -i "$SSH_KEY" -o BatchMode=yes -o ConnectTimeout=20 \
  "$LOCAL_TMP" "${BACKUP_USER}@${BACK_HOST}:${BACKUP_DIR}/${FILENAME}" \
  || err "scp fejlede"

# ------------------- FJERN GAMLE BACKUPS -------------------
echo "Fjerner backups ældre end ${RETENTION_DAYS} dage på backup-hosten..."
ssh -i "$SSH_KEY" -o BatchMode=yes "${BACKUP_USER}@${BACK_HOST}" \
  "find '${BACKUP_DIR}' -maxdepth 1 -type f -name '*.sql.gz' -mtime +${RETENTION_DAYS} -print -delete || true"

# ------------------- FÆRDIG -------------------
echo "Backup færdig: ${BACK_HOST}:${BACKUP_DIR}/${FILENAME}"
