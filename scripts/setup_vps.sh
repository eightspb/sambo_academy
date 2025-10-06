#!/bin/bash

# Скрипт для первоначальной настройки VPS
# Устанавливает Docker, Docker Compose и все необходимые зависимости

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 VPS Setup Script for Sambo Academy${NC}"
echo "=========================================="
echo ""

# Проверка, что скрипт запущен на VPS (а не локально)
if [ -f "docker-compose.yml" ]; then
    echo -e "${YELLOW}⚠️  Похоже, вы запускаете скрипт локально.${NC}"
    echo "Этот скрипт нужно запускать на VPS!"
    echo ""
    read -p "Продолжить? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}📦 Обновление системы...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo -e "${GREEN}🐳 Установка Docker...${NC}"

# Удалить старые версии
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Установить зависимости
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Добавить Docker GPG ключ
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Добавить репозиторий Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установить Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Добавить текущего пользователя в группу docker
sudo usermod -aG docker $USER

echo ""
echo -e "${GREEN}✅ Docker установлен!${NC}"
docker --version
docker compose version

echo ""
echo -e "${GREEN}🔧 Настройка системы...${NC}"

# Установить дополнительные инструменты
sudo apt-get install -y git htop nano wget ufw

# Настроить firewall
echo -e "${YELLOW}🔥 Настройка firewall...${NC}"
sudo ufw --force enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw status

echo ""
echo -e "${GREEN}📁 Создание директорий...${NC}"
mkdir -p ~/sambo_academy
mkdir -p ~/sambo_academy/backups
mkdir -p ~/sambo_academy/logs

echo ""
echo -e "${GREEN}✅ Настройка VPS завершена!${NC}"
echo ""
echo -e "${YELLOW}⚠️  ВАЖНО:${NC}"
echo "1. Перелогиньтесь (logout/login) чтобы группа docker применилась"
echo "2. Или выполните: newgrp docker"
echo ""
echo -e "${BLUE}Следующий шаг:${NC}"
echo "Запустите скрипт deploy.sh для деплоя приложения"
