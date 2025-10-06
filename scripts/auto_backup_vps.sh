#!/bin/bash

# Автоматический бэкап БД на VPS
# Запускается через cron ежедневно

set -e

# Директория для бэкапов
BACKUP_DIR="/home/slava/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/sambo_backup_$DATE.sql"

# Создать директорию если не существует
mkdir -p $BACKUP_DIR

# Создать бэкап
cd /home/slava/sambo_academy
docker compose -f docker-compose.production.yml exec -T db pg_dump -U sambo_user sambo_academy > $BACKUP_FILE

# Сжать бэкап
gzip $BACKUP_FILE

# Создать симлинк на последний бэкап
ln -sf "${BACKUP_FILE}.gz" "$BACKUP_DIR/latest.sql.gz"

# Удалить бэкапы старше 30 дней
find $BACKUP_DIR -name "sambo_backup_*.sql.gz" -mtime +30 -delete

# Вывести результат
echo "$(date): Бэкап создан - ${BACKUP_FILE}.gz ($(du -h ${BACKUP_FILE}.gz | cut -f1))" >> $BACKUP_DIR/backup.log

# Показать последние 5 бэкапов
ls -lh $BACKUP_DIR/sambo_backup_*.sql.gz 2>/dev/null | tail -5 >> $BACKUP_DIR/backup.log
