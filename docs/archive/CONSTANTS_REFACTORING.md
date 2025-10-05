# 🔧 Рефакторинг: Централизация констант приложения

## ✨ Что изменилось

Все хардкоженные константы и дефолтные значения вынесены в **единый файл констант** `app/constants.py`.

---

## ❌ Проблема до рефакторинга

### Хардкод был разбросан по файлам:

1. **`app/api/settings.py`** - дефолтные цены `3500`, `3000`, `5000`, `4200`
2. **`templates/settings.html`** - те же значения продублированы
3. **`templates/payments.html`** - еще раз продублированы
4. **`init_settings.py`** - снова те же константы

**Проблемы:**
- ❌ Дублирование кода
- ❌ Сложно изменить значение (нужно править в 4 местах)
- ❌ Высокий риск ошибок и рассинхронизации
- ❌ Нарушение принципа DRY (Don't Repeat Yourself)

---

## ✅ Решение: Централизованные константы

### Создан файл `app/constants.py`

Все константы приложения теперь в одном месте:

```python
# app/constants.py

# Default subscription prices
DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE = 3500
DEFAULT_SUBSCRIPTION_8_JUNIOR_PRICE = 3000
DEFAULT_SUBSCRIPTION_12_SENIOR_PRICE = 5000
DEFAULT_SUBSCRIPTION_12_JUNIOR_PRICE = 4200

# Settings keys
SETTING_KEY_SUBSCRIPTION_8_SENIOR = "subscription_8_senior_price"
SETTING_KEY_SUBSCRIPTION_8_JUNIOR = "subscription_8_junior_price"
SETTING_KEY_SUBSCRIPTION_12_SENIOR = "subscription_12_senior_price"
SETTING_KEY_SUBSCRIPTION_12_JUNIOR = "subscription_12_junior_price"

# Settings descriptions
SETTING_DESC_SUBSCRIPTION_8_SENIOR = "Стоимость абонемента на 8 занятий для старших"
SETTING_DESC_SUBSCRIPTION_8_JUNIOR = "Стоимость абонемента на 8 занятий для младших"
SETTING_DESC_SUBSCRIPTION_12_SENIOR = "Стоимость абонемента на 12 занятий для старших"
SETTING_DESC_SUBSCRIPTION_12_JUNIOR = "Стоимость абонемента на 12 занятий для младших"

# ... и другие константы
```

---

## 📋 Категории констант

### 💰 Subscription Prices (Цены абонементов)
- Дефолтные цены для всех типов
- Диапазоны цен для UI подсказок

### ⚙️ Settings Keys (Ключи настроек)
- Ключи для хранения в БД
- Описания настроек

### 📄 Pagination (Пагинация)
- Размер страницы по умолчанию
- Максимальный размер страницы

### 🔐 Session (Сессии)
- Срок действия сессии
- Ограничения пароля

### 📊 Subscription Types (Типы абонементов)
- `8_sessions`, `12_sessions`

### 👥 Group Types (Типы групп)
- Возрастные группы: `senior`, `junior`
- Типы расписания: `mon_wed_fri`, `tue_thu`
- Уровни подготовки: `beginner`, `experienced`

### ✅ Attendance Status (Статусы посещаемости)
- `present`, `absent`, `excused`, `late`

### 💳 Payment Status (Статусы платежей)
- `paid`, `pending`, `overdue`

### 💵 Payment Types (Типы платежей)
- `cash`, `card`, `transfer`

---

## 🔄 Обновленные файлы

### Backend:

1. **`app/constants.py`** ⭐ НОВЫЙ
   - Единый источник всех констант

2. **`app/api/settings.py`**
   - Импортирует константы вместо хардкода
   - Использует `DEFAULT_SUBSCRIPTION_*_PRICE` и `SETTING_KEY_*`

3. **`init_settings.py`**
   - Импортирует константы
   - Нет хардкоженных значений

### Frontend:

4. **`templates/settings.html`**
   - Убран хардкод дефолтных значений
   - Загружает цены только из API

5. **`templates/payments.html`**
   - Убран хардкод дефолтных значений
   - Загружает цены только из API
   - Добавлена проверка `subscriptionPrices !== null`

---

## 💡 Преимущества

### ✅ Единая точка изменения
Чтобы изменить дефолтную цену, нужно поправить только один файл:
```python
# app/constants.py
DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE = 3700  # Было 3500
```

### ✅ Отсутствие дублирования
Каждая константа определена один раз.

### ✅ Типобезопасность
Импорт констант проверяется IDE и линтерами.

### ✅ Легкая поддержка
Все константы в одном месте, легко найти и изменить.

### ✅ Масштабируемость
Легко добавлять новые константы.

---

## 📝 Примеры использования

### Backend (Python):

```python
from app.constants import (
    DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE,
    SETTING_KEY_SUBSCRIPTION_8_SENIOR
)

# Использование дефолтного значения
price = DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE

# Использование ключа
setting_key = SETTING_KEY_SUBSCRIPTION_8_SENIOR
```

### Frontend (JavaScript):

```javascript
// Загрузка из API (НЕ хардкод!)
const prices = await api.get('/settings/prices');
const price = prices.subscription_8_senior_price;
```

---

## 🎯 Принципы

### DRY (Don't Repeat Yourself)
Каждое знание имеет единственное, недвусмысленное представление в системе.

### Single Source of Truth
Один источник правды для каждой константы.

### Separation of Concerns
Константы отделены от бизнес-логики.

---

## ⚠️ Важные правила

### ❌ НЕ делайте так:

```python
# ❌ Плохо - хардкод
price = 3500
```

```javascript
// ❌ Плохо - хардкод
const defaultPrice = 3500;
```

### ✅ Делайте так:

```python
# ✅ Хорошо - использование констант
from app.constants import DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE
price = DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE
```

```javascript
// ✅ Хорошо - загрузка из API
const prices = await api.get('/settings/prices');
const price = prices.subscription_8_senior_price;
```

---

## 🚀 Будущие улучшения

В будущем можно добавить в `constants.py`:

- Лимиты для валидации (мин/макс цены, длины имен и т.д.)
- Форматы дат и времени
- Роли пользователей
- Сообщения об ошибках
- Email шаблоны
- URL паттерны
- И другие константы приложения

---

## 📊 Статистика рефакторинга

- **Создано:** 1 новый файл (`app/constants.py`)
- **Обновлено:** 4 файла
- **Удалено хардкода:** ~20 мест
- **Добавлено констант:** 30+
- **Время на изменение дефолтной цены:** с 5 минут до 10 секунд

---

**Готово! Константы централизованы и код стал чище! 🎉**
