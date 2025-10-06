# 🚀 Руководство по деплою Sambo Academy на VPS

## 📋 Предварительные требования

- VPS с Ubuntu 20.04/22.04 (у вас: 193.42.124.51)
- SSH доступ к серверу (уже настроен в `.env`)
- Git установлен локально
- Docker и Docker Compose будут установлены автоматически **на VPS**

## 📍 Где что запускается?

### **[ЛОКАЛЬНО]** - Ваш компьютер:
- Все скрипты: `bash scripts/deploy.sh`, `bash scripts/monitor.sh`
- Редактирование файлов `.env.production`
- Скрипты **автоматически** подключаются к VPS через SSH

### **[VPS]** - Сервер 193.42.124.51:
- Docker контейнеры (app, db, nginx)
- Production база данных
- Nginx веб-сервер

**💡 Важно:** Вам НЕ нужно вручную подключаться к VPS!  
Все скрипты запускаются локально и сами делают всё на VPS.

---

## 🔧 Подготовка к деплою

### Шаг 1: **[ЛОКАЛЬНО]** Настройка .env.production

⚠️ **Важно понимать про пароли БД:**

**У вас есть 2 окружения:**
1. **Локальное** (разработка) - файл `.env`:
   - Пароль: `sambo_password` (простой, для разработки)
   - База: на вашем компьютере
   - **НЕ трогаем этот файл!**

2. **Production** (VPS) - файл `.env.production`:
   - Пароль: **НОВЫЙ** надежный (для безопасности)
   - База: на VPS сервере
   - **Настраиваем сейчас!**

**Что произойдет:**
- Локальная БД → создается дамп (все данные)
- На VPS → создается НОВАЯ БД с НОВЫМ паролем
- Дамп → загружается в новую БД на VPS
- **Результат:** Все данные на VPS, но с безопасным паролем!

### Настройка .env.production:

```bash
# [ЛОКАЛЬНО] Сгенерировать секретный ключ:
openssl rand -hex 32

# [ЛОКАЛЬНО] Открыть файл:
nano .env.production
```

**ОБЯЗАТЕЛЬНО измените:**

```bash
# 1. Вставить сгенерированный ключ (32+ символа):
SECRET_KEY=ваш_сгенерированный_ключ_минимум_32_символа

# 2. Придумать НОВЫЙ надежный пароль для production БД:
#    (НЕ используйте sambo_password - это для разработки!)
POSTGRES_PASSWORD=Strong_Production_Password_2024!

# 3. Обновить DATABASE_URL с тем же НОВЫМ паролем:
DATABASE_URL=postgresql+asyncpg://sambo_user:Strong_Production_Password_2024!@localhost:5432/sambo_academy
```

**Опционально:** укажите домен
```bash
DOMAIN=your-domain.com
```

### Шаг 2: **[ЛОКАЛЬНО]** Создание бэкапа локальной БД

```bash
# [ЛОКАЛЬНО] Создать дамп текущей БД
bash scripts/backup_db.sh
```

Дамп будет сохранен в `backups/sambo_academy_backup_YYYYMMDD_HHMMSS.sql`

**Что в дампе:**
- Все студенты
- Все группы
- Все платежи
- Все посещаемость
- Все пользователи
- И т.д.

## 🚀 Автоматический деплой

### Первый деплой (с нуля)

```bash
# [ЛОКАЛЬНО] Запустить интерактивный скрипт деплоя
bash scripts/deploy.sh

# Выбрать: 1) Полный деплой (первый раз)
```

**Что делает скрипт пошагово:**

```
[ЛОКАЛЬНО] 1. ✅ Создаст бэкап локальной БД
   → backups/sambo_academy_backup_YYYYMMDD.sql

[ЛОКАЛЬНО] 2. ✅ Проверит настройки .env.production
   
[ЛОКАЛЬНО → VPS] 3. ✅ Подключится к VPS через SSH
   → Использует данные из .env (SSH=vbazar1t@193.42.124.51/...)
   
[VPS] 4. ✅ Создаст директорию ~/sambo_academy на VPS
   
[VPS] 5. ✅ Клонирует код с GitHub на VPS
   → git clone github.com/eightspb/sambo_academy
   
[ЛОКАЛЬНО → VPS] 6. ✅ Загрузит .env.production на VPS
   → Скопирует как ~/sambo_academy/.env (на VPS)
   
[ЛОКАЛЬНО → VPS] 7. ✅ Загрузит дамп БД на VPS
   → Скопирует backup.sql на VPS
   
[VPS] 8. ✅ Запустит Docker Compose на VPS
   → docker compose up -d (app, db, nginx)
   
[VPS] 9. ✅ Дождется запуска БД (~10 сек)
   
[VPS] 10. ✅ Восстановит БД из дампа на VPS
   → Все ваши данные теперь в БД на VPS
   → С новым паролем из .env.production
   
[VPS] 11. ✅ Проверит статус всех контейнеров
```

**Время выполнения:** ~2-3 минуты

**Результат:**
- ✅ Приложение работает на http://193.42.124.51
- ✅ Все данные перенесены
- ✅ Production БД с надежным паролем
- ✅ Nginx настроен
- ✅ Всё готово к использованию!

### Обновление приложения

```bash
bash scripts/deploy.sh
```

Доступные опции:
- **1) Полный деплой** - первая установка
- **2) Обновить код** - обновить только код приложения
- **3) Обновить код + БД** - обновить код и загрузить новый дамп БД
- **4) Только БД** - обновить только данные БД
- **5) Перезапустить** - перезапустить приложение

## 📊 Мониторинг

### Просмотр логов и статуса

```bash
bash scripts/monitor.sh
```

Доступные опции:
- **1) Статус контейнеров** - проверить работу сервисов
- **2) Логи приложения** - посмотреть логи FastAPI
- **3) Логи БД** - посмотреть логи PostgreSQL
- **4) Логи Nginx** - посмотреть логи веб-сервера
- **5) Ресурсы** - использование CPU/RAM/Disk
- **6) SSH** - подключиться к серверу напрямую

## 🔧 Ручная настройка VPS (опционально)

Если нужно настроить VPS вручную:

```bash
# 1. Подключиться к VPS
ssh user@your-vps-ip

# 2. Запустить скрипт настройки
bash ~/sambo_academy/scripts/setup_vps.sh

# 3. Перелогиниться
exit
ssh user@your-vps-ip
```

## 🌐 Настройка домена и SSL

### Если у вас есть домен:

1. **Настройте DNS:**
   ```
   A запись: your-domain.com → IP вашего VPS
   ```

2. **Измените nginx конфиг:**
   ```bash
   # На VPS
   nano ~/sambo_academy/nginx/conf.d/sambo.conf
   
   # Замените server_name _ на:
   server_name your-domain.com;
   ```

3. **Получите SSL сертификат:**
   ```bash
   # На VPS
   cd ~/sambo_academy
   
   # Установить certbot
   sudo apt-get install certbot python3-certbot-nginx
   
   # Получить сертификат
   sudo certbot --nginx -d your-domain.com
   ```

4. **Перезапустить nginx:**
   ```bash
   docker compose -f docker-compose.production.yml restart nginx
   ```

## 🔒 Безопасность

### Рекомендации:

1. **Измените SSH пароль на VPS**
   ```bash
   passwd
   ```

2. **Настройте SSH ключи (рекомендуется)**
   ```bash
   ssh-copy-id user@vps-ip
   ```

3. **Регулярно обновляйте систему**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

4. **Настройте автоматические бэкапы БД**
   ```bash
   # Добавить в crontab на VPS:
   0 2 * * * cd ~/sambo_academy && docker compose -f docker-compose.production.yml exec -T db pg_dump -U sambo_user sambo_academy > ~/backups/backup_$(date +\%Y\%m\%d).sql
   ```

## 📝 Структура файлов деплоя

```
sambo_academy/
├── .env.production              # Production конфигурация (НЕ коммитить!)
├── docker-compose.production.yml # Docker Compose для production
├── nginx/
│   └── conf.d/
│       └── sambo.conf           # Nginx конфигурация
├── scripts/
│   ├── backup_db.sh             # Бэкап локальной БД
│   ├── deploy.sh                # Главный скрипт деплоя
│   ├── monitor.sh               # Мониторинг VPS
│   └── setup_vps.sh             # Настройка VPS
└── backups/                     # Дампы БД
```

## 🆘 Troubleshooting

### Приложение не запускается

```bash
# Проверить логи
bash scripts/monitor.sh
# Выбрать: 2) Показать логи приложения

# Проверить статус контейнеров
docker compose -f docker-compose.production.yml ps

# Перезапустить
docker compose -f docker-compose.production.yml restart
```

### БД не подключается

```bash
# Проверить логи БД
bash scripts/monitor.sh
# Выбрать: 3) Показать логи БД

# Проверить переменные окружения
docker compose -f docker-compose.production.yml exec app env | grep DATABASE
```

### Ошибка при восстановлении БД

```bash
# Подключиться к VPS
ssh user@vps-ip

# Проверить дамп
head ~/sambo_academy/backup.sql

# Восстановить вручную
cd ~/sambo_academy
docker compose -f docker-compose.production.yml exec -T db psql -U sambo_user sambo_academy < backup.sql
```

## 📞 Полезные команды

```bash
# Подключиться к БД
docker compose -f docker-compose.production.yml exec db psql -U sambo_user sambo_academy

# Посмотреть логи в реальном времени
docker compose -f docker-compose.production.yml logs -f app

# Перезапустить все
docker compose -f docker-compose.production.yml restart

# Остановить все
docker compose -f docker-compose.production.yml down

# Запустить заново
docker compose -f docker-compose.production.yml up -d
```

## ✅ Checklist перед деплоем

- [ ] Настроен `.env.production` с надежными паролями
- [ ] Создан бэкап локальной БД
- [ ] SSH доступ к VPS работает
- [ ] VPS имеет минимум 1GB RAM
- [ ] Открыты порты 80 и 443
- [ ] (Опционально) Настроен домен
- [ ] Приложение протестировано локально

---

**🎉 После успешного деплоя приложение будет доступно по адресу вашего VPS!**

Например: `http://193.42.124.51` или `https://your-domain.com`
