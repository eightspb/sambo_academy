# 🔒 Настройка SSL для Sambo Academy

## Требования

- ✅ Домен: `sambo-academy.ru` должен быть настроен и указывать на IP `193.42.124.51`
- ✅ Порты 80 и 443 должны быть открыты на сервере

## Шаг 1: Проверка DNS

Убедитесь, что домен указывает на ваш сервер:

```bash
dig +short sambo-academy.ru
# Должен вернуть: 193.42.124.51
```

## Шаг 2: Запуск скрипта установки SSL

На VPS выполните:

```bash
ssh slava@193.42.124.51
cd ~/sambo_academy

# Сделать скрипт исполняемым
chmod +x scripts/setup_ssl.sh

# Запустить установку SSL
./scripts/setup_ssl.sh
```

Скрипт автоматически:
1. Остановит nginx
2. Получит SSL сертификат от Let's Encrypt
3. Запустит nginx с SSL конфигурацией

## Шаг 3: Проверка

После успешной установки ваш сайт будет доступен по адресу:

- ✅ **https://sambo-academy.ru** (основной)
- ✅ **http://sambo-academy.ru** (перенаправление на HTTPS)
- ✅ **http://193.42.124.51** (перенаправление на HTTPS)

## Автообновление сертификата

Certbot контейнер автоматически проверяет и обновляет сертификаты каждые 12 часов.

Для ручного обновления:

```bash
docker compose -f docker-compose.production.yml run --rm certbot renew
docker compose -f docker-compose.production.yml restart nginx
```

## Проверка SSL

Проверьте качество SSL конфигурации:
https://www.ssllabs.com/ssltest/analyze.html?d=sambo-academy.ru

Должна быть оценка **A** или **A+**

## Устранение проблем

### Ошибка: "DNS resolution failed"

Проверьте DNS запись:
```bash
nslookup sambo-academy.ru
```

### Ошибка: "Port 80 already in use"

Остановите nginx:
```bash
docker compose -f docker-compose.production.yml stop nginx
```

### Ошибка: "Rate limit exceeded"

Let's Encrypt имеет лимит 5 попыток в час. Подождите и попробуйте снова.

## Файлы конфигурации

- `nginx/conf.d/sambo.conf` - Nginx конфигурация с SSL
- `certbot/conf/` - SSL сертификаты
- `certbot/www/` - Webroot для Certbot challenge
- `docker-compose.production.yml` - Certbot сервис

## Что дальше?

После установки SSL:

1. ✅ Обновите ссылки в документации на HTTPS
2. ✅ Настройте Service Worker для PWA (если нужен offline режим)
3. ✅ Добавьте домен в манифест PWA (`static/manifest.json`)
4. ✅ Проверьте работу на мобильных устройствах

## Важные примечания

- 🔒 Сертификаты Let's Encrypt действительны **90 дней**
- 🔄 Автообновление настроено в docker-compose
- 📧 Email в скрипте `setup_ssl.sh` используется для уведомлений от Let's Encrypt
- 🌐 Поддерживаются оба варианта: `sambo-academy.ru` и `www.sambo-academy.ru`
