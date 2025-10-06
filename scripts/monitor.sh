#!/bin/bash

# Скрипт для мониторинга приложения на VPS
# Показывает логи, статус и ресурсы

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Загрузить конфигурацию из .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Проверить наличие SSH переменных
if [ -z "$SSH_USER" ] || [ -z "$SSH_HOST" ] || [ -z "$SSH_PORT" ] || [ -z "$SSH_PASS" ]; then
    echo -e "${RED}❌ SSH переменные не найдены в .env${NC}"
    echo "Нужны: SSH_USER, SSH_HOST, SSH_PORT, SSH_PASS"
    exit 1
fi

SSH_CMD="sshpass -p '$SSH_PASS' ssh -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST"

echo -e "${BLUE}📊 Sambo Academy - Monitor${NC}"
echo "============================"
echo ""

echo -e "${YELLOW}Выберите действие:${NC}"
echo "1) Показать статус контейнеров"
echo "2) Показать логи приложения"
echo "3) Показать логи БД"
echo "4) Показать логи Nginx"
echo "5) Показать использование ресурсов"
echo "6) Подключиться к VPS (SSH)"
echo ""
read -p "Ваш выбор (1-6): " choice

case $choice in
    1)
        echo -e "${GREEN}📦 Статус контейнеров:${NC}"
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml ps'"
        echo ""
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml top'"
        ;;
        
    2)
        echo -e "${GREEN}📋 Логи приложения (последние 50 строк):${NC}"
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml logs --tail=50 app'"
        ;;
        
    3)
        echo -e "${GREEN}📋 Логи БД (последние 50 строк):${NC}"
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml logs --tail=50 db'"
        ;;
        
    4)
        echo -e "${GREEN}📋 Логи Nginx (последние 50 строк):${NC}"
        eval "$SSH_CMD 'cd ~/sambo_academy && docker compose -f docker-compose.production.yml logs --tail=50 nginx'"
        ;;
        
    5)
        echo -e "${GREEN}💻 Использование ресурсов:${NC}"
        echo ""
        echo -e "${YELLOW}Системные ресурсы:${NC}"
        eval "$SSH_CMD 'free -h && echo && df -h && echo'"
        echo ""
        echo -e "${YELLOW}Docker контейнеры:${NC}"
        eval "$SSH_CMD 'docker stats --no-stream'"
        ;;
        
    6)
        echo -e "${GREEN}🔗 Подключение к VPS...${NC}"
        echo -e "${YELLOW}Для выхода используйте: exit${NC}"
        echo ""
        sshpass -p "$SSH_PASS" ssh -p $SSH_PORT $SSH_USER@$SSH_HOST
        ;;
        
    *)
        echo -e "${RED}❌ Неверный выбор!${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✨ Готово!${NC}"
