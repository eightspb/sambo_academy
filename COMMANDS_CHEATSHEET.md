# 📝 Шпаргалка по командам деплоя

## 📍 ВАЖНО: Где что запускается

### [ЛОКАЛЬНО] - Все эти команды на ВАШЕМ компьютере:
- `bash scripts/deploy.sh` ← деплой
- `bash scripts/monitor.sh` ← мониторинг
- `bash scripts/backup_db.sh` ← бэкап
- `nano .env.production` ← настройка

### [VPS] - Автоматически или через SSH:
- Docker контейнеры
- База данных
- Nginx

**💡 Скрипты запускаются локально, но работают на VPS через SSH!**

---

## 🚀 Первый деплой (пошагово)

### 1. **[ЛОКАЛЬНО]** Сгенерировать секретный ключ
```bash
openssl rand -hex 32
```

### 2. **[ЛОКАЛЬНО]** Настроить .env.production
```bash
nano .env.production

# Вставить сгенерированный ключ в SECRET_KEY
# Придумать НОВЫЙ надежный пароль для production БД
# (НЕ тот что в .env - это для разработки!)
POSTGRES_PASSWORD=new_strong_password_2024
```

⚠️ **Про пароли БД:**
- `.env` (локальный) - `sambo_password` - НЕ трогаем!
- `.env.production` (VPS) - НОВЫЙ пароль - настраиваем!
- Данные переносятся через дамп автоматически

### 3. **[ЛОКАЛЬНО]** Запустить деплой
```bash
bash scripts/deploy.sh
```
Выбрать: **1) Полный деплой (первый раз)**

---

## 🔄 Регулярные операции

### Обновить код на VPS
```bash
# [ЛОКАЛЬНО] Закоммитить изменения
git add .
git commit -m "Update"
git push

# [ЛОКАЛЬНО] Обновить на VPS
bash scripts/deploy.sh
# → 2) Обновить код
```

### Обновить код + БД
```bash
# [ЛОКАЛЬНО]
bash scripts/deploy.sh
# → 3) Обновить код + БД
```

### Обновить только БД
```bash
# [ЛОКАЛЬНО]
bash scripts/deploy.sh
# → 4) Только БД
```

### Перезапустить приложение
```bash
# [ЛОКАЛЬНО]
bash scripts/deploy.sh
# → 5) Перезапустить приложение
```

---

## 📊 Мониторинг

### Посмотреть статус контейнеров
```bash
# [ЛОКАЛЬНО] Запускаете локально, показывает статус VPS
bash scripts/monitor.sh
# → 1) Показать статус контейнеров
```

### Посмотреть логи приложения
```bash
# [ЛОКАЛЬНО]
bash scripts/monitor.sh
# → 2) Показать логи приложения
```

### Посмотреть логи БД
```bash
# [ЛОКАЛЬНО]
bash scripts/monitor.sh
# → 3) Показать логи БД
```

### Посмотреть логи Nginx
```bash
# [ЛОКАЛЬНО]
bash scripts/monitor.sh
# → 4) Показать логи Nginx
```

### Посмотреть использование ресурсов
```bash
# [ЛОКАЛЬНО]
bash scripts/monitor.sh
# → 5) Показать использование ресурсов
```

### Подключиться к VPS
```bash
# [ЛОКАЛЬНО] Откроет SSH сессию к VPS
bash scripts/monitor.sh
# → 6) Подключиться к VPS (SSH)
```

---

## 💾 Работа с БД

### Создать бэкап локальной БД
```bash
# [ЛОКАЛЬНО] Создает дамп вашей локальной БД
bash scripts/backup_db.sh
```

### Посмотреть список бэкапов
```bash
# [ЛОКАЛЬНО]
ls -lh backups/
```

### Загрузить бэкап на VPS вручную
```bash
# [ЛОКАЛЬНО] Копирует файл на VPS
scp backups/latest.sql vbazar1t@193.42.124.51:~/sambo_academy/
```

### Восстановить БД на VPS вручную
```bash
# [ЛОКАЛЬНО] Подключиться к VPS
ssh vbazar1t@193.42.124.51

# [VPS] Восстановить БД
cd ~/sambo_academy
docker compose -f docker-compose.production.yml exec -T db psql -U sambo_user sambo_academy < backup.sql
```

---

## 🐳 Docker команды на VPS

⚠️ **Эти команды выполняются НА VPS после SSH подключения**

### Зайти на VPS
```bash
# [ЛОКАЛЬНО] Подключиться
ssh vbazar1t@193.42.124.51

# [VPS] Перейти в директорию приложения
cd ~/sambo_academy
```

### Посмотреть статус контейнеров
```bash
# [VPS]
docker compose -f docker-compose.production.yml ps
```

### Посмотреть логи
```bash
# Все логи
docker compose -f docker-compose.production.yml logs

# Только приложение
docker compose -f docker-compose.production.yml logs app

# Последние 50 строк с обновлением
docker compose -f docker-compose.production.yml logs -f --tail=50 app
```

### Перезапустить сервисы
```bash
# Всё
docker compose -f docker-compose.production.yml restart

# Только приложение
docker compose -f docker-compose.production.yml restart app

# Только БД
docker compose -f docker-compose.production.yml restart db

# Только Nginx
docker compose -f docker-compose.production.yml restart nginx
```

### Остановить/Запустить
```bash
# Остановить всё
docker compose -f docker-compose.production.yml down

# Запустить всё
docker compose -f docker-compose.production.yml up -d

# Пересобрать и запустить
docker compose -f docker-compose.production.yml up -d --build
```

### Подключиться к контейнеру
```bash
# К приложению
docker compose -f docker-compose.production.yml exec app bash

# К БД
docker compose -f docker-compose.production.yml exec db psql -U sambo_user sambo_academy
```

---

## 🔍 Диагностика проблем

### Приложение не отвечает
```bash
# 1. Проверить статус
docker compose -f docker-compose.production.yml ps

# 2. Посмотреть логи
docker compose -f docker-compose.production.yml logs app --tail=100

# 3. Перезапустить
docker compose -f docker-compose.production.yml restart app
```

### БД не подключается
```bash
# Проверить что БД запущена
docker compose -f docker-compose.production.yml ps db

# Проверить логи БД
docker compose -f docker-compose.production.yml logs db --tail=50

# Проверить что пароль совпадает в .env
cat .env | grep POSTGRES_PASSWORD
```

### Nginx не проксирует
```bash
# Проверить конфиг
docker compose -f docker-compose.production.yml exec nginx nginx -t

# Перезапустить Nginx
docker compose -f docker-compose.production.yml restart nginx

# Посмотреть логи
docker compose -f docker-compose.production.yml logs nginx
```

---

## 🌐 Работа с доменом и SSL

### Получить SSL сертификат (на VPS)
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Обновить SSL сертификат
```bash
sudo certbot renew
```

### Проверить когда истекает сертификат
```bash
sudo certbot certificates
```

---

## 📈 Мониторинг ресурсов

### Использование диска
```bash
ssh vbazar1t@193.42.124.51 'df -h'
```

### Использование памяти
```bash
ssh vbazar1t@193.42.124.51 'free -h'
```

### Статистика Docker
```bash
ssh vbazar1t@193.42.124.51 'docker stats --no-stream'
```

### Размер Docker образов
```bash
ssh vbazar1t@193.42.124.51 'docker images'
```

### Очистить неиспользуемые образы
```bash
ssh vbazar1t@193.42.124.51 'docker system prune -a'
```

---

## 🔐 Безопасность

### Изменить SSH пароль (на VPS)
```bash
passwd
```

### Настроить SSH ключи (рекомендуется)
```bash
# Локально
ssh-keygen -t ed25519
ssh-copy-id vbazar1t@193.42.124.51

# Теперь можно подключаться без пароля
ssh vbazar1t@193.42.124.51
```

### Проверить открытые порты
```bash
ssh vbazar1t@193.42.124.51 'sudo ufw status'
```

---

## 🎯 Полезные алиасы (добавить в ~/.bashrc)

```bash
# Деплой
alias deploy='bash ~/WORK/CascadeProjects/sambo_academy/scripts/deploy.sh'

# Мониторинг
alias monitor='bash ~/WORK/CascadeProjects/sambo_academy/scripts/monitor.sh'

# Бэкап
alias backup='bash ~/WORK/CascadeProjects/sambo_academy/scripts/backup_db.sh'

# SSH к VPS
alias vps='ssh vbazar1t@193.42.124.51'

# После добавления:
source ~/.bashrc
```

---

## 📞 Быстрые команды

| Команда | Действие |
|---------|----------|
| `bash scripts/deploy.sh` | Деплой |
| `bash scripts/monitor.sh` | Мониторинг |
| `bash scripts/backup_db.sh` | Бэкап БД |
| `ssh vbazar1t@193.42.124.51` | SSH |
| `http://193.42.124.51` | Открыть приложение |

---

**💡 Совет:** Держите эту шпаргалку под рукой для быстрого доступа к командам!
