#!/bin/bash

# Скрипт резервного копирования базы данных
# Создает дамп локальной БД для переноса на VPS

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🗄️  Backup Database Script${NC}"
echo "================================"

# Путь к файлу дампа
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/sambo_academy_backup_$TIMESTAMP.sql"

# Создать директорию для бэкапов если не существует
mkdir -p $BACKUP_DIR

# Получить имя контейнера БД
DB_CONTAINER=$(docker-compose ps -q db)

if [ -z "$DB_CONTAINER" ]; then
    echo -e "${RED}❌ Контейнер БД не запущен!${NC}"
    echo "Запустите: docker-compose up -d db"
    exit 1
fi

echo -e "${YELLOW}📦 Создание дампа базы данных...${NC}"

# Создать дамп БД
docker exec $DB_CONTAINER pg_dump -U sambo_user sambo_academy > $BACKUP_FILE

# Проверить успешность
if [ $? -eq 0 ]; then
    FILESIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Дамп успешно создан!${NC}"
    echo "   Файл: $BACKUP_FILE"
    echo "   Размер: $FILESIZE"
    
    # Создать символическую ссылку на последний бэкап
    ln -sf "$(basename $BACKUP_FILE)" "$BACKUP_DIR/latest.sql"
    echo -e "${GREEN}🔗 Создан алиас: $BACKUP_DIR/latest.sql${NC}"
else
    echo -e "${RED}❌ Ошибка при создании дампа!${NC}"
    exit 1
fi

# Показать список всех бэкапов
echo ""
echo -e "${YELLOW}📋 Список всех бэкапов:${NC}"
ls -lh $BACKUP_DIR/*.sql 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'

echo ""
echo -e "${GREEN}✨ Готово! Используйте этот файл для восстановления на VPS.${NC}"
