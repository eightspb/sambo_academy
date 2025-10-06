# 🎯 Sambo Academy - Production Deployment

Автоматизированная система деплоя на VPS с поддержкой бэкапов и мониторинга.

## 📦 Что включено

- ✅ Автоматический деплой на VPS в 1 команду
- ✅ Бэкап и восстановление базы данных
- ✅ Docker Compose с Nginx
- ✅ Мониторинг и логи
- ✅ Поддержка SSL/HTTPS
- ✅ Готовая production конфигурация

## 🚀 Быстрый старт

### Шаг 1: Настройте .env.production

```bash
cp .env.production .env.production.local
nano .env.production.local

# Измените пароли и секреты
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=your_strong_password
```

### Шаг 2: Деплой

```bash
bash scripts/deploy.sh
```

Выберите **"1) Полный деплой"** для первого запуска.

### Шаг 3: Откройте приложение

```
http://ваш-vps-ip:80
```

## 📚 Документация

- **[QUICK_START_DEPLOY.md](QUICK_START_DEPLOY.md)** - Быстрый старт (3 минуты)
- **[DEPLOY.md](DEPLOY.md)** - Полная документация по деплою

## 🛠️ Доступные скрипты

| Скрипт | Описание |
|--------|----------|
| `scripts/deploy.sh` | Главный скрипт деплоя |
| `scripts/backup_db.sh` | Создание бэкапа БД |
| `scripts/monitor.sh` | Мониторинг VPS |
| `scripts/setup_vps.sh` | Настройка VPS с нуля |

## 🏗️ Архитектура Production

```
VPS (Ubuntu 22.04)
├── Nginx (reverse proxy, SSL)
│   ├── Port 80 → HTTP
│   └── Port 443 → HTTPS
│
├── FastAPI App (Docker)
│   └── Port 8000
│
└── PostgreSQL (Docker)
    └── Port 5432 (internal)
```

## 📊 Управление

### Обновление кода

```bash
bash scripts/deploy.sh
# Выбрать: 2) Обновить код
```

### Обновление БД

```bash
bash scripts/deploy.sh
# Выбрать: 4) Только БД
```

### Просмотр логов

```bash
bash scripts/monitor.sh
# Выбрать: 2) Показать логи приложения
```

### Подключение к VPS

```bash
bash scripts/monitor.sh
# Выбрать: 6) Подключиться к VPS (SSH)
```

## 🔒 Безопасность

- ⚠️ `.env.production` в `.gitignore` (не коммитится)
- ✅ Надежные пароли для БД
- ✅ SECRET_KEY для JWT токенов
- ✅ Firewall (UFW) настроен автоматически
- ✅ SSL/HTTPS готов к настройке

## 📁 Структура

```
sambo_academy/
├── scripts/
│   ├── backup_db.sh       # Бэкап БД
│   ├── deploy.sh          # Деплой
│   ├── monitor.sh         # Мониторинг
│   └── setup_vps.sh       # Настройка VPS
├── nginx/
│   ├── nginx.conf         # Основной конфиг
│   └── conf.d/
│       └── sambo.conf     # Конфиг приложения
├── docker-compose.production.yml
├── .env.production        # Пример конфига (коммитится)
├── .env.production.local  # Ваш конфиг (НЕ коммитится)
├── DEPLOY.md             # Полная документация
└── QUICK_START_DEPLOY.md # Быстрый старт
```

## 🎓 Примеры использования

### Первый деплой

```bash
# 1. Настроить пароли
nano .env.production

# 2. Запустить деплой
bash scripts/deploy.sh
# → 1) Полный деплой

# Готово! Приложение работает
```

### Регулярное обновление

```bash
# Изменили код локально
git add .
git commit -m "Added new feature"
git push

# Обновить на VPS
bash scripts/deploy.sh
# → 2) Обновить код
```

### Бэкап БД перед важными изменениями

```bash
# Создать бэкап
bash scripts/backup_db.sh

# Обновить БД
bash scripts/deploy.sh
# → 4) Только БД
```

## 🌐 Настройка домена (опционально)

```bash
# 1. Настроить DNS
# A запись: your-domain.com → ваш_VPS_IP

# 2. Изменить nginx конфиг
ssh your-vps
nano ~/sambo_academy/nginx/conf.d/sambo.conf
# server_name your-domain.com;

# 3. Получить SSL
sudo certbot --nginx -d your-domain.com

# 4. Перезапустить
cd ~/sambo_academy
docker compose -f docker-compose.production.yml restart nginx
```

## 🐛 Troubleshooting

### Приложение не запускается

```bash
bash scripts/monitor.sh
# → 2) Показать логи приложения
```

### БД не подключается

```bash
# Проверить пароль в .env.production
# Проверить логи БД
bash scripts/monitor.sh
# → 3) Показать логи БД
```

### Ошибка подключения к VPS

```bash
# Проверить SSH в .env
cat .env | grep SSH

# Попробовать подключиться вручную
ssh user@vps-ip
```

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте [DEPLOY.md](DEPLOY.md) - раздел Troubleshooting
2. Посмотрите логи: `bash scripts/monitor.sh`
3. Подключитесь к VPS: `bash scripts/monitor.sh` → 6

## ✅ Checklist перед деплоем

- [ ] `.env.production` настроен с надежными паролями
- [ ] SSH доступ к VPS работает (указан в `.env`)
- [ ] Локальная БД работает и содержит актуальные данные
- [ ] Код закоммичен и запушен на GitHub
- [ ] VPS имеет минимум 1GB RAM
- [ ] Открыты порты 80 и 443

## 🚀 Production Features

- **Multi-worker FastAPI** - 4 worker процесса
- **Nginx** - reverse proxy с gzip
- **PostgreSQL** - persistent storage
- **Auto-restart** - контейнеры перезапускаются автоматически
- **Health checks** - проверка работоспособности БД
- **Logging** - централизованные логи
- **SSL ready** - готов к настройке HTTPS

---

**Сделано с ❤️ для Sambo Academy**

VPS: `193.42.124.51`  
Repository: `github.com/eightspb/sambo_academy`
