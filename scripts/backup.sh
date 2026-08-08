#!/bin/bash
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "💾 Backing up database..."
docker-compose exec -T db pg_dump -U aiworkforce ai_workforce > "$BACKUP_DIR/db_$TIMESTAMP.sql"

echo "💾 Backing up Redis..."
docker-compose exec -T redis redis-cli BGSAVE

echo "✅ Backup complete: $BACKUP_DIR/db_$TIMESTAMP.sql"
