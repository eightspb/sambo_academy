# 🚀 Деплой на VPS

## Как это работает

**Все команды запускаются на вашем компьютере** - скрипты сами подключаются к VPS через SSH.

VPS: `193.42.124.51` (уже настроен в `.env`)

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
DATABASE_URL=postgresql+asyncpg://sambo_user:тот_же_пароль@localhost:5432/sambo_academy
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

```bash
# Создать бэкап локальной БД
bash scripts/backup_db.sh

# Посмотреть бэкапы
ls -lh backups/
```

---

## 🐳 Docker команды (на VPS)

Если нужно что-то сделать вручную:

```bash
# Подключиться к VPS
ssh vbazar1t@193.42.124.51
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

### Приложение не запускается
```bash
bash scripts/monitor.sh
# → 2) Показать логи приложения
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
# Посмотреть что в .env
cat .env | grep SSH

# Попробовать подключиться вручную
ssh vbazar1t@193.42.124.51
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
