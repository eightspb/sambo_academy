# 🚀 Деплой на VPS

## Как это работает

**Все команды запускаются на вашем компьютере** - скрипты сами подключаются к VPS через SSH.

VPS настроен в `.env`:
```bash
SSH_USER=slava
SSH_HOST=193.42.124.51
SSH_PORT=22
SSH_PASS=bfXdvE_P&22R
```

---

## 📋 Быстрый старт

### 1. Настроить пароли

```bash
# Сгенерировать секретный ключ
openssl rand -hex 32

# Открыть конфиг
nano .env.production
```

**Изменить:**
```bash
SECRET_KEY=вставьте_сгенерированный_ключ_32_символа
POSTGRES_PASSWORD=придумайте_надежный_пароль
# ⚠️ ВАЖНО: используйте 'db' вместо 'localhost' для Docker!
DATABASE_URL=postgresql+asyncpg://sambo_user:тот_же_пароль@db:5432/sambo_academy
```

**Про пароли БД:**
- `.env` - ваш локальный пароль (`sambo_password`) - **НЕ трогать!**
- `.env.production` - НОВЫЙ пароль для VPS - **настроить сейчас!**
- Данные переносятся через дамп автоматически

### 2. Запустить деплой

```bash
bash scripts/deploy.sh
```

Выбрать: **1) Полный деплой (первый раз)**

### 3. Готово!

Приложение: `http://193.42.124.51`

**Время деплоя: ~2-3 минуты**

---

## 🔄 Обновления

```bash
# Обновить код
bash scripts/deploy.sh
# → 2) Обновить код

# Обновить код + БД
bash scripts/deploy.sh
# → 3) Обновить код + БД

# Перезапустить
bash scripts/deploy.sh
# → 5) Перезапустить приложение
```

---

## 📊 Мониторинг

```bash
bash scripts/monitor.sh
```

**Опции:**
- 1) Статус контейнеров
- 2) Логи приложения
- 3) Логи БД
- 4) Логи Nginx
- 5) Использование ресурсов
- 6) SSH к VPS

---

## 💾 Бэкап БД

### Ручной бэкап (локально)

```bash
# Создать бэкап локальной БД
bash scripts/backup_db.sh

# Посмотреть бэкапы
ls -lh backups/
```

### Автоматический ежедневный бэкап (на VPS)

```bash
# Настроить автобэкап (один раз)
bash scripts/setup_auto_backup.sh
```

**Что настраивается:**
- ⏰ Ежедневный бэкап в 3:00 утра (cron)
- 📁 Сохранение в `~/backups/` на VPS
- 🗑️ Автоудаление бэкапов старше 30 дней
- 📝 Лог в `~/backups/backup.log`

**Проверка:**
```bash
# Посмотреть логи
ssh slava@193.42.124.51 'cat ~/backups/backup.log'

# Список бэкапов
ssh slava@193.42.124.51 'ls -lh ~/backups/'

# Скачать последний бэкап
scp -P 22 slava@193.42.124.51:~/backups/latest.sql.gz ./backups/
```
### 🔄 Восстановление из бэкапа

Если нужно восстановить БД из автобэкапа:

```bash
# Скачать бэкап
scp -P 22 slava@193.42.124.51:~/backups/latest.sql.gz ./backups/

# Распаковать
gunzip ./backups/latest.sql.gz

# Восстановить на VPS
ssh slava@193.42.124.51
cd sambo_academy
docker compose -f docker-compose.production.yml stop app
docker compose -f docker-compose.production.yml exec -T db psql -U sambo_user -d postgres -c 'DROP DATABASE sambo_academy;'
docker compose -f docker-compose.production.yml exec -T db psql -U sambo_user -d postgres -c 'CREATE DATABASE sambo_academy;'
docker compose -f docker-compose.production.yml exec -T db psql -U sambo_user sambo_academy < backup.sql
docker compose -f docker-compose.production.yml start app
```

---

## 🐳 Docker команды (на VPS)

Если нужно что-то сделать вручную:

```bash
# Подключиться к VPS
ssh slava@193.42.124.51
cd ~/sambo_academy

# Статус
docker compose -f docker-compose.production.yml ps

# Логи
docker compose -f docker-compose.production.yml logs app

# Перезапуск
docker compose -f docker-compose.production.yml restart

# Остановить
docker compose -f docker-compose.production.yml down

# Запустить
docker compose -f docker-compose.production.yml up -d
```

---

## 🌐 Домен и SSL (опционально)

Если хотите домен вместо IP:

1. **Настроить DNS:** `your-domain.com → 193.42.124.51`

2. **Изменить nginx:**
   ```bash
   ssh vbazar1t@193.42.124.51
   nano ~/sambo_academy/nginx/conf.d/sambo.conf
   # Изменить: server_name your-domain.com;
   ```

3. **Получить SSL:**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

4. **Перезапустить nginx:**
   ```bash
   cd ~/sambo_academy
   docker compose -f docker-compose.production.yml restart nginx
   ```

---

## 🆘 Проблемы

### Сброс пароля администратора

Если забыли пароль:

```bash
# Локально - загрузить скрипт на VPS
scp -P 22 reset_admin_password.py slava@193.42.124.51:~/sambo_academy/

# На VPS - скопировать в контейнер и запустить
ssh slava@193.42.124.51
cd sambo_academy
docker compose -f docker-compose.production.yml cp reset_admin_password.py app:/app/
docker compose -f docker-compose.production.yml exec app python reset_admin_password.py admin новый_пароль
```

**Пример:**
```bash
docker compose -f docker-compose.production.yml exec app python reset_admin_password.py admin admin123
# ✅ Пароль изменен на: admin123
```

### Порт 80 занят (address already in use)
```bash
# Подключиться к VPS
ssh slava@193.42.124.51

# Остановить системный nginx
sudo systemctl stop nginx
sudo systemctl disable nginx

# Запустить контейнеры
cd sambo_academy
docker compose -f docker-compose.production.yml up -d
```

### Приложение не запускается (502 Bad Gateway)
```bash
bash scripts/monitor.sh
# → 2) Показать логи приложения

# Если видите "Connection refused" - проверьте DATABASE_URL
# Должно быть: @db:5432 (не @localhost:5432)
```

### БД не подключается
```bash
bash scripts/monitor.sh
# → 3) Показать логи БД

# Проверить пароль
cat .env.production | grep POSTGRES_PASSWORD
```

### Ошибка при деплое
```bash
# Посмотреть SSH настройки
cat .env | grep SSH

# Попробовать подключиться вручную
ssh slava@193.42.124.51
```

---

## ✅ Checklist

Перед деплоем:
- [ ] `.env.production` настроен (пароли изменены)
- [ ] Локальная БД работает и содержит данные
- [ ] Код закоммичен на GitHub

Готово к деплою:
```bash
bash scripts/deploy.sh
```
