#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PROJECT_DIR="$SCRIPT_DIR"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y-%m-%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "[$(date)] === STARTING AUTOMATIC BACKUP ==="

# 1. Dump PostgreSQL
docker exec agromachines_db pg_dump -U agroprom_admin -d agroprom_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
echo "[$(date)] PostgreSQL database dumped successfully."

# 2. Backup MinIO volume (handles both agromachines_minio_data and legacy backend_minio_data)
MINIO_VOL=$(docker volume ls -q | grep -E "minio_data" | head -n 1)
if [ -n "$MINIO_VOL" ]; then
  docker run --rm \
    -v "$MINIO_VOL":/volume \
    -v "$BACKUP_DIR":/backup \
    alpine tar czf /backup/media_$DATE.tar.gz -C /volume .
  echo "[$(date)] MinIO media files backed up successfully from volume $MINIO_VOL."
else
  echo "[$(date)] WARNING: MinIO volume not found, skipping media backup."
fi

# 3. Clean up old audit logs (>90 days)
docker exec agromachines_db psql -U agroprom_admin -d agroprom_db -c "DELETE FROM audit_logs WHERE timestamp < NOW() - INTERVAL '90 days';"
echo "[$(date)] Old audit logs (older than 90 days) deleted from database."

# 4. Rotate old backups (>30 days)
find "$BACKUP_DIR" -type f -mtime +30 -delete
echo "[$(date)] Old backups deleted (retained last 30 days)."

echo "[$(date)] === BACKUP PROCESS COMPLETED SUCCESSFULLY ==="
