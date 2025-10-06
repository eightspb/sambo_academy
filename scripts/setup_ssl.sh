#!/bin/bash

# Скрипт для настройки SSL сертификата Let's Encrypt
# Запускается на VPS

set -e

DOMAIN="sambo-academy.ru"
EMAIL="admin@sambo-academy.ru"  # Измените на ваш email

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔒 Настройка SSL для $DOMAIN${NC}"
echo "===================================="
echo ""

# Проверка что скрипт запущен на VPS
if [ ! -f "docker-compose.production.yml" ]; then
    echo -e "${RED}❌ Запустите этот скрипт на VPS в директории sambo_academy${NC}"
    exit 1
fi

# 1. Создать директории для certbot
echo -e "${YELLOW}📁 Создание директорий...${NC}"
mkdir -p certbot/conf
mkdir -p certbot/www

# 2. Проверить DNS
echo -e "${YELLOW}🌐 Проверка DNS записи...${NC}"
RESOLVED_IP=$(dig +short $DOMAIN | tail -1)
SERVER_IP=$(curl -s ifconfig.me)

echo "Домен $DOMAIN указывает на: $RESOLVED_IP"
echo "IP сервера: $SERVER_IP"

if [ "$RESOLVED_IP" != "$SERVER_IP" ]; then
    echo -e "${RED}⚠️  Предупреждение: DNS может быть настроен неправильно${NC}"
    echo "Продолжить? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        exit 1
    fi
fi

# 3. Остановить nginx для получения сертификата
echo -e "${YELLOW}⏸️  Остановка nginx...${NC}"
docker compose -f docker-compose.production.yml stop nginx

# 4. Получить сертификат
echo -e "${YELLOW}🔐 Получение SSL сертификата...${NC}"
docker run --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  -p 80:80 \
  certbot/certbot certonly \
  --standalone \
  --preferred-challenges http \
  --email $EMAIL \
  --agree-tos \
  --non-interactive \
  --no-eff-email \
  -d $DOMAIN

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Ошибка при получении сертификата${NC}"
    docker compose -f docker-compose.production.yml start nginx
    exit 1
fi

echo -e "${GREEN}✅ Сертификат получен успешно!${NC}"

# 5. Запустить nginx
echo -e "${YELLOW}▶️  Запуск nginx с SSL...${NC}"
docker compose -f docker-compose.production.yml start nginx

echo ""
echo -e "${GREEN}🎉 SSL успешно настроен!${NC}"
echo ""
echo -e "${BLUE}Ваш сайт доступен по адресам:${NC}"
echo "  🌐 https://$DOMAIN"
echo "  🌐 http://$DOMAIN (перенаправление на HTTPS)"
echo ""
echo -e "${YELLOW}📝 Автообновление сертификата:${NC}"
echo "Добавьте в crontab:"
echo "0 3 * * * cd ~/sambo_academy && docker compose -f docker-compose.production.yml run --rm certbot renew && docker compose -f docker-compose.production.yml restart nginx"
