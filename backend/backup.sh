#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

PROJECT_DIR=$(dirname "$SCRIPT_DIR")
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y-%m-%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "[$(date)] === STARTING AUTOMATIC BACKUP ==="

docker exec agromachines_db pg_dump -U agroprom_admin -d agroprom_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
echo "[$(date)] PostgreSQL database dumped successfully."

docker run --rm \
  -v backend_minio_data:/volume \
  -v "$BACKUP_DIR":/backup \
  alpine tar czf /backup/media_$DATE.tar.gz -C /volume .
echo "[$(date)] MinIO media files backed up successfully."

find "$BACKUP_DIR" -type f -mtime +30 -delete
echo "[$(date)] Old backups deleted (retained last 30 days)."

echo "[$(date)] === BACKUP PROCESS COMPLETED SUCCESSFULLY ==="
