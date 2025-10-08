# 🔧 Инструкция системного администратора - Sambo Academy

**Версия:** 1.0
**Дата:** 08.10.2025

---

## 🎯 Содержание

1. [Введение](#введение)
2. [Установка и настройка](#установка-и-настройка)
3. [Конфигурация системы](#конфигурация-системы)
4. [Управление базами данных](#управление-базами-данных)
5. [Мониторинг и логи](#мониторинг-и-логи)
6. [Безопасность сервера](#безопасность-сервера)
7. [Резервное копирование](#резервное-копирование)
8. [Масштабирование](#масштабирование)
9. [Обновления](#обновления)
10. [Диагностика проблем](#диагностика-проблем)

---

## 🚀 Введение

Как **системный администратор** вы отвечаете за:

- ✅ **Развертывание** и настройку инфраструктуры
- ✅ **Обеспечение безопасности** сервера и данных
- ✅ **Мониторинг производительности** и доступности
- ✅ **Резервное копирование** и восстановление
- ✅ **Масштабирование** системы при росте нагрузки
- ✅ **Обновление** компонентов системы

### Требуемые навыки:
- 🔧 Docker и Docker Compose
- 🐘 PostgreSQL администрирование
- 🌐 Nginx веб-сервер
- 🔒 SSL/TLS сертификаты
- 📊 Мониторинг и логирование
- 🛡️ Безопасность Linux

---

## 💻 Установка и настройка

### Системные требования:

**Минимальные:**
- CPU: 2 ядра
- RAM: 4 GB
- Disk: 20 GB SSD
- OS: Ubuntu 22.04 LTS / Debian 11

**Рекомендуемые:**
- CPU: 4 ядра
- RAM: 8 GB
- Disk: 50 GB SSD
- OS: Ubuntu 22.04 LTS

### Предварительная установка:

1. **Обновите систему:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Установите необходимые пакеты:**
   ```bash
   sudo apt install -y curl wget git htop nano ufw fail2ban
   ```

3. **Установите Docker:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo systemctl enable docker
   sudo systemctl start docker
   ```

4. **Установите Docker Compose:**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

### Развертывание приложения:

1. **Клонируйте репозиторий:**
   ```bash
   cd /home
   git clone https://github.com/eightspb/sambo_academy.git
   cd sambo_academy
   ```

2. **Настройте переменные окружения:**
   ```bash
   cp .env.example .env.production
   nano .env.production
   ```

3. **Обязательные настройки в .env.production:**
   ```bash
   # Безопасность
   SECRET_KEY=ваш_случайный_ключ_минимум_32_символа

   # База данных
   POSTGRES_DB=sambo_academy
   POSTGRES_USER=sambo_user
   POSTGRES_PASSWORD=сложный_пароль_минимум_16_символов

   # Домены
   FRONTEND_URL=https://sambo-academy.ru
   BACKEND_URL=https://api.sambo-academy.ru

   # SSL
   SSL_CERT_PATH=/etc/letsencrypt/live/sambo-academy.ru/fullchain.pem
   SSL_KEY_PATH=/etc/letsencrypt/live/sambo-academy.ru/privkey.pem
   ```

4. **Создайте первого администратора:**
   ```bash
   sudo docker-compose -f docker-compose.production.yml run --rm app python create_admin.py
   ```

5. **Запустите приложение:**
   ```bash
   sudo docker-compose -f docker-compose.production.yml up -d
   ```

---

## ⚙️ Конфигурация системы

### Файлы конфигурации:

#### docker-compose.production.yml:
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

  app:
    build: .
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl.conf:/etc/nginx/ssl.conf
      - ${SSL_CERT_PATH}:/etc/ssl/certs/sambo-academy.ru.crt
      - ${SSL_KEY_PATH}:/etc/ssl/private/sambo-academy.ru.key
```

#### nginx.conf:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server app:8000;
    }

    server {
        listen 80;
        server_name sambo-academy.ru;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name sambo-academy.ru;

        ssl_certificate /etc/ssl/certs/sambo-academy.ru.crt;
        ssl_certificate_key /etc/ssl/private/sambo-academy.ru.key;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### Настройка SSL сертификатов:

1. **Установите certbot:**
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   ```

2. **Получите сертификат:**
   ```bash
   sudo certbot --nginx -d sambo-academy.ru
   ```

3. **Настройте автоматическое обновление:**
   ```bash
   sudo crontab -e
   # Добавьте: 0 3 * * * certbot renew --quiet
   ```

---

## 🗄️ Управление базами данных

### Структура базы данных:

#### Основные таблицы:
- **users** - пользователи системы
- **groups** - группы тренировок
- **students** - ученики
- **subscriptions** - абонементы
- **attendances** - посещения
- **payments** - платежи
- **tournaments** - турниры

#### Связи между таблицами:
```
users (1) ─── (M) groups
groups (1) ─── (M) students
students (1) ─── (M) subscriptions
students (1) ─── (M) attendances
students (1) ─── (M) payments
tournaments (1) ─── (M) tournament_participations
```

### Миграции базы данных:

#### Создание миграции:
```bash
sudo docker-compose exec app alembic revision --autogenerate -m "Описание изменений"
```

#### Применение миграций:
```bash
sudo docker-compose exec app alembic upgrade head
```

#### Откат миграции:
```bash
sudo docker-compose exec app alembic downgrade -1
```

### Оптимизация производительности:

1. **Индексы:**
   ```sql
   CREATE INDEX idx_attendance_date ON attendances(session_date);
   CREATE INDEX idx_payments_month ON payments(payment_month);
   ```

2. **VACUUM:**
   ```bash
   sudo docker-compose exec db vacuumdb -U sambo_user -d sambo_academy --full
   ```

3. **Анализ таблиц:**
   ```bash
   sudo docker-compose exec db psql -U sambo_user -d sambo_academy -c "ANALYZE;"
   ```

---

## 📊 Мониторинг и логи

### Настройка мониторинга:

#### Prometheus + Grafana:

1. **Установите:**
   ```bash
   sudo apt install -y prometheus grafana
   ```

2. **Настройте prometheus.yml:**
   ```yaml
   global:
     scrape_interval: 15s

   scrape_configs:
     - job_name: 'sambo_academy'
       static_configs:
         - targets: ['localhost:8000']
   ```

#### Мониторинг Docker контейнеров:
```bash
# CPU и память
docker stats

# Логи всех контейнеров
sudo docker-compose logs -f

# Логи конкретного сервиса
sudo docker-compose logs -f app
```

### Важные метрики для отслеживания:

1. **Производительность:**
   - CPU usage контейнеров
   - Memory consumption
   - Disk I/O
   - Network traffic

2. **Доступность:**
   - HTTP response time
   - Error rates
   - Database connection pool

3. **Безопасность:**
   - Failed login attempts
   - Suspicious IP addresses
   - Unusual traffic patterns

### Настройка алертов:

**Email уведомления:**
```bash
sudo apt install -y msmtp
# Настройте ~/.msmtprc
```

**Telegram уведомления:**
```bash
pip install requests
# Создайте скрипт мониторинга
```

---

## 🔒 Безопасность сервера

### Базовая защита:

1. **Firewall:**
   ```bash
   sudo ufw enable
   sudo ufw allow ssh
   sudo ufw allow http
   sudo ufw allow https
   sudo ufw allow 22,80,443/tcp
   ```

2. **Fail2ban:**
   ```bash
   sudo apt install -y fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

3. **Автоматические обновления:**
   ```bash
   sudo apt install -y unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

### Безопасность Docker:

1. **Пользователь без root:**
   ```dockerfile
   RUN useradd -m appuser
   USER appuser
   ```

2. **Минимизация образа:**
   ```bash
   FROM python:3.11-slim
   # Установите только необходимые пакеты
   ```

3. **Секреты в окружении:**
   ```bash
   # Никогда не храните секреты в коде
   SECRET_KEY=your_secret_key
   ```

### Мониторинг безопасности:

1. **Проверка логов:**
   ```bash
   sudo journalctl -u docker -f
   sudo tail -f /var/log/auth.log
   ```

2. **Аудит системы:**
   ```bash
   sudo apt install -y auditd
   sudo systemctl enable auditd
   ```

---

## 💾 Резервное копирование

### Стратегия резервного копирования:

#### 1. База данных PostgreSQL:
```bash
# Ежедневно
sudo docker-compose exec db pg_dump -U sambo_user sambo_academy > /backups/db_$(date +%Y%m%d).sql

# Еженедельно (полный бэкап)
sudo docker-compose exec db pg_dump -U sambo_user --clean --if-exists sambo_academy > /backups/db_full_$(date +%Y%m%d).sql
```

#### 2. Файлы приложения:
```bash
# Ежедневно
sudo tar -czf /backups/app_$(date +%Y%m%d).tar.gz /home/sambo_academy/

# Конфигурация
sudo tar -czf /backups/config_$(date +%Y%m%d).tar.gz /home/sambo_academy/.env* /home/sambo_academy/docker-compose*
```

#### 3. Автоматизация:
```bash
# Создайте скрипт /home/sambo_academy/scripts/backup.sh
#!/bin/bash
BACKUP_DIR="/backups"

# База данных
docker-compose exec db pg_dump -U sambo_user sambo_academy > $BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sql

# Файлы
tar -czf $BACKUP_DIR/app_$(date +%Y%m%d_%H%M%S).tar.gz /home/sambo_academy/

# Очистка старых бэкапов (старше 30 дней)
find $BACKUP_DIR -type f -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -type f -name "*.tar.gz" -mtime +30 -delete

# Добавьте в cron: 0 2 * * * /home/sambo_academy/scripts/backup.sh
```

### Восстановление данных:

#### Восстановление базы данных:
```bash
# Остановите приложение
sudo docker-compose down

# Восстановите базу
sudo docker-compose up -d db
sudo docker-compose exec db psql -U sambo_user sambo_academy < backup.sql

# Запустите приложение
sudo docker-compose up -d
```

#### Восстановление файлов:
```bash
# Остановите сервисы
sudo docker-compose down

# Восстановите файлы
sudo tar -xzf backup.tar.gz -C /

# Запустите сервисы
sudo docker-compose up -d
```

---

## 📈 Масштабирование

### Горизонтальное масштабирование:

#### Load Balancer:
```nginx
upstream backend {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 443 ssl;
    location / {
        proxy_pass http://backend;
    }
}
```

#### Несколько инстансов приложения:
```yaml
version: '3.8'
services:
  app1:
    build: .
    environment:
      - INSTANCE_ID=1

  app2:
    build: .
    environment:
      - INSTANCE_ID=2

  app3:
    build: .
    environment:
      - INSTANCE_ID=3
```

### Вертикальное масштабирование:

#### Увеличение ресурсов:
```bash
# Проверьте текущее потребление
docker stats

# Увеличьте лимиты в docker-compose.yml
app:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
```

### Кеширование:

#### Redis для сессий:
```yaml
services:
  redis:
    image: redis:alpine

  app:
    depends_on:
      - redis
    environment:
      REDIS_URL: redis://redis:6379
```

---

## 🔄 Обновления

### Обновление приложения:

1. **Создайте резервную копию:**
   ```bash
   sudo docker-compose exec db pg_dump -U sambo_user sambo_academy > backup_pre_update.sql
   ```

2. **Получите обновления:**
   ```bash
   cd /home/sambo_academy
   git pull origin main
   ```

3. **Обновите зависимости:**
   ```bash
   sudo docker-compose build --no-cache
   ```

4. **Примените миграции базы данных:**
   ```bash
   sudo docker-compose exec app alembic upgrade head
   ```

5. **Перезапустите сервисы:**
   ```bash
   sudo docker-compose down
   sudo docker-compose up -d
   ```

6. **Проверьте работоспособность:**
   ```bash
   curl -f https://sambo-academy.ru/api/health
   ```

### Откат при проблемах:

1. **Восстановите базу данных:**
   ```bash
   sudo docker-compose exec db psql -U sambo_user sambo_academy < backup_pre_update.sql
   ```

2. **Откатите git:**
   ```bash
   git reset --hard HEAD~1
   ```

3. **Пересоберите образ:**
   ```bash
   sudo docker-compose build --no-cache
   sudo docker-compose up -d
   ```

---

## 🔍 Диагностика проблем

### Проверка состояния системы:

#### Docker сервисы:
```bash
# Статус всех контейнеров
sudo docker-compose ps

# Логи приложения
sudo docker-compose logs app

# Логи базы данных
sudo docker-compose logs db

# Логи веб-сервера
sudo docker-compose logs nginx
```

#### Системные ресурсы:
```bash
# Использование диска
df -h

# Использование памяти
free -h

# Загрузка CPU
top -n 1

# Сетевые соединения
netstat -tuln | grep :80
```

### Диагностика базы данных:

#### Производительность запросов:
```sql
-- Включите slow query log
ALTER DATABASE sambo_academy SET log_min_duration_statement = 1000;

-- Проверьте размер таблиц
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### Проверка соединений:
```bash
sudo docker-compose exec db psql -U sambo_user -d sambo_academy -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'sambo_academy';"
```

### Диагностика сети:

#### Проверка DNS:
```bash
nslookup sambo-academy.ru
```

#### Тестирование портов:
```bash
telnet sambo-academy.ru 80
telnet sambo-academy.ru 443
```

#### Проверка сертификатов:
```bash
curl -vI https://sambo-academy.ru
```

### Логи ошибок:

#### Важные файлы логов:
```bash
# Системные логи
sudo journalctl -u docker -f

# Nginx логи
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Fail2ban
sudo fail2ban-client status
```

---

## 🚨 Действия при чрезвычайных ситуациях

### Сервер недоступен:

1. **Проверьте статус сервисов:**
   ```bash
   sudo docker-compose ps
   ```

2. **Проверьте системные ресурсы:**
   ```bash
   df -h && free -h && top -n 1 -b | head -5
   ```

3. **Перезапустите сервисы:**
   ```bash
   sudo docker-compose restart
   ```

### Атака на сервер:

1. **Включите строгий firewall:**
   ```bash
   sudo ufw --force reset
   sudo ufw allow from your_ip to any port 22
   sudo ufw allow 80,443
   sudo ufw enable
   ```

2. **Заблокируйте подозрительные IP:**
   ```bash
   sudo fail2ban-client set nginx-http-auth banip 192.168.1.100
   ```

3. **Уведомите администратора приложения**

### Потеря данных:

1. **Используйте резервные копии**
2. **Восстановите из последней рабочей копии**
3. **Сообщите пользователям о потере данных**

### Проблемы с производительностью:

1. **Проанализируйте использование ресурсов:**
   ```bash
   docker stats
   ```

2. **Проверьте медленные запросы:**
   ```sql
   SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;
   ```

3. **Оптимизируйте конфигурацию**

---

## 📞 Контакты и поддержка

### Эскалация проблем:

**Уровень 1:** Самостоятельное решение (используйте эту инструкцию)
**Уровень 2:** Консультация с администратором приложения
**Уровень 3:** Обращение к разработчикам

### Контактная информация:

**Администратор приложения:** [Имя] [Телефон] [Email]
**Разработчик:** [Имя] [Телефон] [Email]
**Хостинг-провайдер:** [Название] [Телефон поддержки]

### Создание тикета поддержки:

1. **Опишите проблему подробно**
2. **Укажите время возникновения**
3. **Прикрепите логи и скриншоты**
4. **Укажите уровень срочности**

---

## ✅ Чек-лист ежедневного обслуживания

- [ ] Проверить статус всех Docker контейнеров
- [ ] Проверить использование системных ресурсов
- [ ] Просмотреть логи на наличие ошибок
- [ ] Проверить доступность веб-приложения
- [ ] Убедиться в корректной работе базы данных
- [ ] Проверить актуальность резервных копий

## 📚 Полезные ресурсы

- [Docker документация](https://docs.docker.com/)
- [PostgreSQL документация](https://www.postgresql.org/docs/)
- [Nginx документация](https://nginx.org/en/docs/)
- [Prometheus документация](https://prometheus.io/docs/)
- [Linux системное администрирование](https://linux.die.net/man/)

---

**Спасибо за обеспечение стабильной работы Sambo Academy! 🥋**

*Эта инструкция обновляется по мере развития инфраструктуры. Последняя версия всегда доступна в репозитории проекта.*
