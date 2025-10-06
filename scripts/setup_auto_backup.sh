#!/bin/bash

# Скрипт для настройки автоматического ежедневного бэкапа на VPS
# Запускается ЛОКАЛЬНО

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Загрузить конфигурацию
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Проверить SSH переменные
if [ -z "$SSH_USER" ] || [ -z "$SSH_HOST" ] || [ -z "$SSH_PORT" ] || [ -z "$SSH_PASS" ]; then
    echo -e "${RED}❌ SSH переменные не найдены в .env${NC}"
    exit 1
fi

SSH_CMD="sshpass -p '$SSH_PASS' ssh -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST"

echo -e "${BLUE}🔧 Настройка автоматического бэкапа на VPS${NC}"
echo "===================================="
echo ""

# 1. Создать директорию для бэкапов
echo -e "${YELLOW}📁 Создание директории для бэкапов...${NC}"
$SSH_CMD "mkdir -p ~/backups"

# 2. Загрузить скрипт бэкапа на VPS
echo -e "${YELLOW}📤 Загрузка скрипта бэкапа...${NC}"
scp -P $SSH_PORT -o StrictHostKeyChecking=no scripts/auto_backup_vps.sh $SSH_USER@$SSH_HOST:~/backup_db.sh

# 3. Сделать скрипт исполняемым
echo -e "${YELLOW}🔑 Настройка прав...${NC}"
$SSH_CMD "chmod +x ~/backup_db.sh"

# 4. Проверить существующие cron задачи
echo -e "${YELLOW}📋 Проверка существующих cron задач...${NC}"
$SSH_CMD "crontab -l 2>/dev/null | grep -v backup_db.sh > /tmp/mycron || true"

# 5. Добавить новую cron задачу (ежедневно в 3:00 утра)
echo -e "${YELLOW}⏰ Добавление cron задачи...${NC}"
$SSH_CMD "echo '0 3 * * * /home/$SSH_USER/backup_db.sh >> /home/$SSH_USER/backups/backup.log 2>&1' >> /tmp/mycron"

# 6. Установить cron
$SSH_CMD "crontab /tmp/mycron && rm /tmp/mycron"

echo ""
echo -e "${GREEN}✅ Автоматический бэкап настроен!${NC}"
echo ""
echo -e "${BLUE}Настройки:${NC}"
echo "  📁 Директория: ~/backups/"
echo "  ⏰ Расписание: Ежедневно в 3:00 утра"
echo "  🗑️  Хранение: 30 дней"
echo "  📝 Лог: ~/backups/backup.log"
echo ""

# 7. Создать первый тестовый бэкап
echo -e "${YELLOW}🧪 Создание тестового бэкапа...${NC}"
$SSH_CMD "~/backup_db.sh"

echo ""
echo -e "${GREEN}✅ Тестовый бэкап создан успешно!${NC}"
echo ""

# 8. Показать список бэкапов
echo -e "${BLUE}📦 Текущие бэкапы:${NC}"
$SSH_CMD "ls -lh ~/backups/*.gz 2>/dev/null | tail -5 || echo 'Нет бэкапов'"

echo ""
echo -e "${GREEN}🎉 Готово!${NC}"
echo ""
echo -e "${YELLOW}Полезные команды:${NC}"
echo "  # Просмотр логов бэкапа:"
echo "  ssh $SSH_USER@$SSH_HOST 'cat ~/backups/backup.log'"
echo ""
echo "  # Список бэкапов:"
echo "  ssh $SSH_USER@$SSH_HOST 'ls -lh ~/backups/'"
echo ""
echo "  # Скачать последний бэкап:"
echo "  scp -P $SSH_PORT $SSH_USER@$SSH_HOST:~/backups/latest.sql.gz ./backups/"
echo ""
echo "  # Изменить расписание:"
echo "  ssh $SSH_USER@$SSH_HOST 'crontab -e'"
