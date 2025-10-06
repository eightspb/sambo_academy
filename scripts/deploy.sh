#!/bin/bash

# Главный скрипт деплоя на VPS
# Автоматически деплоит приложение на сервер

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Загрузить конфигурацию из .env если существует
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Парсинг SSH строки из .env
# Формат: user@host/password&port
if [ -z "$SSH" ]; then
    echo -e "${RED}❌ SSH переменная не найдена в .env${NC}"
    exit 1
fi

# Извлечь данные из SSH строки
SSH_USER=$(echo $SSH | cut -d'@' -f1)
SSH_REST=$(echo $SSH | cut -d'@' -f2)
SSH_HOST=$(echo $SSH_REST | cut -d'/' -f1)
SSH_PASS_PORT=$(echo $SSH_REST | cut -d'/' -f2)
SSH_PASS=$(echo $SSH_PASS_PORT | cut -d'&' -f1)
SSH_PORT=$(echo $SSH_PASS_PORT | cut -d'&' -f2)

echo -e "${BLUE}🚀 Sambo Academy - Deploy Script${NC}"
echo "===================================="
echo ""
echo -e "${YELLOW}Сервер:${NC} $SSH_USER@$SSH_HOST:$SSH_PORT"
echo ""

# Проверка наличия sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}📦 Установка sshpass...${NC}"
    sudo apt-get install -y sshpass
fi

# Создать алиас SSH команды с паролем
SSH_CMD="sshpass -p '$SSH_PASS' ssh -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST"
SCP_CMD="sshpass -p '$SSH_PASS' scp -P $SSH_PORT -o StrictHostKeyChecking=no"

# Тест подключения
echo -e "${YELLOW}🔗 Проверка подключения к VPS...${NC}"
if eval "$SSH_CMD 'echo Connected successfully'"; then
    echo -e "${GREEN}✅ Подключение успешно!${NC}"
else
    echo -e "${RED}❌ Ошибка подключения к VPS!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📋 Выберите действие:${NC}"
echo "1) Полный деплой (первый раз)"
echo "2) Обновить код"
echo "3) Обновить код + БД"
echo "4) Только БД"
echo "5) Перезапустить приложение"
echo ""
read -p "Ваш выбор (1-5): " choice

case $choice in
    1)
        echo -e "${GREEN}🚀 Полный деплой...${NC}"
        
        # 1. Создать бэкап БД локально
        echo -e "${YELLOW}📦 Создание бэкапа БД...${NC}"
        bash scripts/backup_db.sh
        
        # 2. Подготовить .env.production
        if [ ! -f .env.production ]; then
            echo -e "${RED}❌ Файл .env.production не найден!${NC}"
            echo "Создайте его на основе .env.production и настройте пароли"
            exit 1
        fi
        
        echo -e "${YELLOW}⚠️  Убедитесь, что вы настроили .env.production${NC}"
        read -p "Продолжить? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        
        # 3. Создать директорию на VPS
        echo -e "${YELLOW}📁 Создание директорий на VPS...${NC}"
        eval "$SSH_CMD 'mkdir -p ~/sambo_academy'"
        
        # 4. Клонировать репозиторий
        echo -e "${YELLOW}📥 Клонирование репозитория...${NC}"
        eval "$SSH_CMD 'cd ~ && rm -rf sambo_academy_temp && git clone https://github.com/eightspb/sambo_academy.git sambo_academy_temp && rm -rf sambo_academy/.git && cp -r sambo_academy_temp/* sambo_academy/ && rm -rf sambo_academy_temp'"
        
        # 5. Загрузить .env.production
        echo -e "${YELLOW}⚙️  Загрузка конфигурации...${NC}"
        eval "$SCP_CMD .env.production $SSH_USER@$SSH_HOST:~/sambo_academy/.env"
        
        # 6. Загрузить дамп БД
        echo -e "${YELLOW}💾 Загрузка дампа БД...${NC}"
        LATEST_BACKUP=$(ls -t backups/*.sql | head -1)
        eval "$SCP_CMD $LATEST_BACKUP $SSH_USER@$SSH_HOST:~/sambo_academy/backup.sql"
        
        # 7. Запустить Docker Compose
        echo -e "${YELLOW}🐳 Запуск приложения...${NC}"
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml up -d --build'"
        
        # 8. Подождать пока БД запустится
        echo -e "${YELLOW}⏳ Ожидание запуска БД...${NC}"
        sleep 10
        
        # 9. Восстановить БД
        echo -e "${YELLOW}📥 Восстановление БД...${NC}"
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml exec -T db psql -U sambo_user sambo_academy < backup.sql'"
        
        echo -e "${GREEN}✅ Полный деплой завершен!${NC}"
        ;;
        
    2)
        echo -e "${GREEN}🔄 Обновление кода...${NC}"
        
        eval "$SSH_CMD 'cd ~/sambo_academy && git pull origin main'"
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml up -d --build app'"
        
        echo -e "${GREEN}✅ Код обновлен!${NC}"
        ;;
        
    3)
        echo -e "${GREEN}🔄 Обновление кода + БД...${NC}"
        
        # Бэкап БД
        bash scripts/backup_db.sh
        LATEST_BACKUP=$(ls -t backups/*.sql | head -1)
        
        # Обновить код
        eval "$SSH_CMD 'cd ~/sambo_academy && git pull origin main'"
        
        # Загрузить новый дамп
        eval "$SCP_CMD $LATEST_BACKUP $SSH_USER@$SSH_HOST:~/sambo_academy/backup.sql"
        
        # Остановить приложение
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml stop app'"
        
        # Восстановить БД
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml exec -T db psql -U sambo_user sambo_academy < backup.sql'"
        
        # Запустить приложение
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml up -d --build app'"
        
        echo -e "${GREEN}✅ Код и БД обновлены!${NC}"
        ;;
        
    4)
        echo -e "${GREEN}💾 Обновление БД...${NC}"
        
        bash scripts/backup_db.sh
        LATEST_BACKUP=$(ls -t backups/*.sql | head -1)
        
        eval "$SCP_CMD $LATEST_BACKUP $SSH_USER@$SSH_HOST:~/sambo_academy/backup.sql"
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml exec -T db psql -U sambo_user sambo_academy < backup.sql'"
        
        echo -e "${GREEN}✅ БД обновлена!${NC}"
        ;;
        
    5)
        echo -e "${GREEN}🔄 Перезапуск приложения...${NC}"
        
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml restart app'"
        
        echo -e "${GREEN}✅ Приложение перезапущено!${NC}"
        ;;
        
    *)
        echo -e "${RED}❌ Неверный выбор!${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}📊 Статус сервисов:${NC}"
eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml ps'"

echo ""
echo -e "${GREEN}✨ Готово!${NC}"
echo -e "${YELLOW}Приложение доступно по адресу:${NC} http://$SSH_HOST"
