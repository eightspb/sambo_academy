# 🐛 Исправление ошибок платежей и групп

## Дата: 2025-10-06

---

## 🔴 Проблема 1: На странице платежей у всех отображается "8 занятий"

### Описание
На странице платежей у всех учеников показывался одинаковый тип абонемента (8 занятий), хотя у них были разные абонементы.

### Причина
В базе данных у платежей поле `subscription_id` было `NULL` (платежи не связаны с конкретными абонементами).

**SQL запрос показал:**
```sql
SELECT p.subscription_id, sub.subscription_type
FROM payments p
LEFT JOIN subscriptions sub ON p.subscription_id = sub.id
-- Результат: subscription_id = NULL для всех платежей
```

### Решение
Изменен запрос API `/api/payments/month/{year}/{month}`:
- **Было:** Получать тип абонемента из связи `payment.subscription_id → subscriptions`
- **Стало:** Получать тип абонемента из **активного абонемента студента**

**Новый запрос:**
```python
# Subquery to get active subscription type for each student
active_sub_subquery = (
    select(Subscription.student_id, Subscription.subscription_type)
    .where(Subscription.is_active == True)
    .distinct(Subscription.student_id)
    .order_by(Subscription.student_id, Subscription.start_date.desc())
    .subquery()
)

query = (
    select(Payment, Student.full_name, active_sub_subquery.c.subscription_type)
    .join(Student, Payment.student_id == Student.id)
    .outerjoin(active_sub_subquery, Student.id == active_sub_subquery.c.student_id)
    ...
)
```

### Результат
✅ На странице платежей теперь отображается **реальный тип абонемента каждого студента**

---

## 🔴 Проблема 2: Ошибка при редактировании группы

### Описание
При попытке редактировать группу и изменить тип абонемента возникала ошибка:
```
500 Internal Server Error
SyntaxError: Unexpected token '1', "Internal S"... is not valid JSON
```

### Причина
1. JavaScript всегда отправлял поле `default_subscription_type`, даже если оно не менялось
2. Backend пытался обработать `null` значение как изменение
3. Логика определения изменений была сложной и запутанной

**Было в JavaScript:**
```javascript
data.default_subscription_type = subscriptionType || null;  // Всегда отправляется
```

**Было в Backend:**
```python
update_data = group_data.model_dump(exclude_unset=False)  # Включает все поля
```

### Решение

#### 1. Упрощена логика JavaScript
**Теперь:**
```javascript
const subscriptionType = formData.get('default_subscription_type');
if (subscriptionType) {  // Отправляется только если есть значение
    data.default_subscription_type = subscriptionType;
}
```

#### 2. Упрощена логика Backend
**Теперь:**
```python
update_data = group_data.model_dump(exclude_unset=True)  # Только установленные поля

if 'default_subscription_type' in update_data:
    new_value = update_data['default_subscription_type']
    old_value = group.default_subscription_type
    if new_value != old_value and new_value is not None:
        subscription_type_changed = True
```

### Результат
✅ Группы редактируются без ошибок
✅ Тип абонемента изменяется только когда реально установлен новый тип

---

## 🔧 Измененные файлы

### Backend:
1. **`app/api/payments.py`**
   - Изменен запрос в `get_monthly_payments()`
   - Теперь использует subquery для получения активного абонемента студента

2. **`app/api/groups.py`**
   - Упрощена логика в `update_group()`
   - Убран `model_dump(exclude_unset=False)`

### Frontend:
3. **`templates/groups.html`**
   - Упрощена логика отправки `default_subscription_type`
   - Поле отправляется только если установлено

---

## 🧪 Как проверить

### Проверка платежей:

1. **Откройте:** http://localhost:8000/payments
2. **Выберите месяц** (например, октябрь 2025)
3. **Проверьте таблицу:**
   - Колонка "Абонемент" должна показывать разные типы для разных учеников
   - Например: "8 занятий", "12 занятий", "-"

**Пример правильного отображения:**
```
| Ученик          | Сумма  | Абонемент   | Тип платежа |
|-----------------|--------|-------------|-------------|
| Иван Петров     | 4200₽  | 8 занятий   | Полная      |
| Мария Сидорова  | 4800₽  | 12 занятий  | Полная      |
| Петр Иванов     | 4200₽  | 8 занятий   | Полная      |
```

---

### Проверка редактирования группы:

1. **Откройте:** http://localhost:8000/groups
2. **Нажмите "Редактировать"** на любой группе
3. **Измените тип абонемента:**
   - Было: "8 занятий"
   - Стало: "12 занятий"
4. **Нажмите "Сохранить"**
5. **Проверьте:**
   - ✅ Группа сохранилась без ошибок
   - ✅ В консоли браузера (F12) нет ошибок
   - ✅ В логах Docker видно: `DEBUG: Subscription type CHANGED!`

**Проверка логов Docker:**
```bash
docker-compose logs -f app | grep DEBUG
```

**Ожидаемый вывод:**
```
DEBUG: Subscription type check - Old: 8_sessions, New: 12_sessions
DEBUG: Subscription type CHANGED! Will update students.
```

---

## 📊 SQL запросы для проверки

### Проверить типы абонементов студентов:
```sql
SELECT 
    s.full_name,
    sub.subscription_type,
    sub.is_active
FROM students s
LEFT JOIN subscriptions sub ON sub.student_id = s.id AND sub.is_active = true
ORDER BY s.full_name;
```

### Проверить связь платежей с абонементами:
```sql
SELECT 
    p.id,
    s.full_name,
    p.subscription_id,
    sub.subscription_type as linked_subscription_type,
    active_sub.subscription_type as student_active_subscription
FROM payments p
JOIN students s ON p.student_id = s.id
LEFT JOIN subscriptions sub ON p.subscription_id = sub.id
LEFT JOIN subscriptions active_sub ON active_sub.student_id = s.id AND active_sub.is_active = true
LIMIT 10;
```

### Проверить типы абонементов групп:
```sql
SELECT 
    g.name as group_name,
    g.default_subscription_type,
    COUNT(s.id) as students_count
FROM groups g
LEFT JOIN students s ON s.group_id = g.id AND s.is_active = true
GROUP BY g.id, g.name, g.default_subscription_type
ORDER BY g.name;
```

---

## ⚠️ Важные замечания

### 1. Платежи не связаны с абонементами

В текущей базе данных у всех платежей `subscription_id = NULL`. Это нормально, если:
- Платежи вносятся вручную
- Платежи не создаются автоматически при создании абонемента

Если нужно связывать платежи с абонементами, необходимо:
1. При создании платежа указывать `subscription_id`
2. Или автоматически определять активный абонемент студента

### 2. Множественные активные абонементы

В базе данных обнаружены студенты с **несколькими активными абонементами одновременно**.

**Пример:**
```sql
-- Студент "Бойко Тимофей" имеет 9 активных абонементов!
SELECT * FROM subscriptions 
WHERE student_id = '66cac168-b09d-4b95-8fcb-246b8fedd692' 
AND is_active = true;
-- Результат: 9 строк
```

**Рекомендация:** Добавить уникальный индекс:
```sql
CREATE UNIQUE INDEX idx_one_active_subscription_per_student
ON subscriptions (student_id)
WHERE is_active = true;
```

Или исправить логику создания абонементов, чтобы перед созданием нового деактивировать старые.

### 3. Enum vs String

В базе данных `subscription_type` хранится как `EIGHT_SESSIONS` (enum PostgreSQL), а в коде используется `8_sessions` (строка).

SQLAlchemy автоматически конвертирует между ними:
- **База:** `EIGHT_SESSIONS`, `TWELVE_SESSIONS`
- **Python/JSON:** `8_sessions`, `12_sessions`

Это нормальное поведение SQLAlchemy Enum.

---

## 🎯 Итоговый результат

### До исправления:
❌ На странице платежей у всех "8 занятий"  
❌ Ошибка 500 при редактировании группы  
❌ Тип абонемента не обновлялся  

### После исправления:
✅ На странице платежей правильные типы абонементов для каждого студента  
✅ Редактирование группы работает без ошибок  
✅ Тип абонемента обновляется для всех учеников группы  
✅ Добавлен debug logging для отслеживания изменений  

---

## 🔄 Следующие шаги (опционально)

### 1. Очистить дублирующиеся абонементы
```python
# Скрипт для деактивации дублирующихся абонементов
# Оставить только самый новый активный абонемент для каждого студента
```

### 2. Добавить уникальный индекс
```sql
CREATE UNIQUE INDEX idx_one_active_subscription_per_student
ON subscriptions (student_id)
WHERE is_active = true;
```

### 3. Связывать платежи с абонементами
При создании платежа автоматически устанавливать `subscription_id` = активному абонементу студента.

---

**Статус:** ✅ ИСПРАВЛЕНО  
**Дата:** 2025-10-06  
**Версия:** 1.0
