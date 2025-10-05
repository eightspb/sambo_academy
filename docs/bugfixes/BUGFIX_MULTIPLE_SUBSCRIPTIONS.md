# 🐛 Исправление: Multiple rows were found

## Проблема

### Симптомы:
- ❌ Главная страница не загружается
- ❌ Ошибка 500 Internal Server Error при запросе `/api/students`
- ❌ Страница турниров не работает

### Ошибка в логах:
```
sqlalchemy.exc.MultipleResultsFound: Multiple rows were found when one or none was required
File "/app/app/api/students.py", line 56, in get_students
    active_sub = sub_result.scalar_one_or_none()
```

---

## Причина

В методе `get_students()` (и других методах API) при получении активного абонемента студента использовался метод `scalar_one_or_none()`:

```python
sub_result = await db.execute(sub_query)
active_sub = sub_result.scalar_one_or_none()  # ❌ ОШИБКА!
```

**Проблема:** У студента может быть **несколько активных абонементов** одновременно:
- Старый абонемент еще активен
- Создали новый абонемент
- Не деактивировали старый

Метод `scalar_one_or_none()` ожидает:
- **0 результатов** → возвращает `None` ✅
- **1 результат** → возвращает объект ✅
- **2+ результатов** → **выбрасывает исключение** ❌

---

## Решение

Заменил `scalar_one_or_none()` на `scalars().first()` во всех методах:

```python
sub_result = await db.execute(sub_query)
active_sub = sub_result.scalars().first()  # ✅ ИСПРАВЛЕНО!
```

**Как работает `scalars().first()`:**
- **0 результатов** → возвращает `None` ✅
- **1 результат** → возвращает объект ✅
- **2+ результатов** → возвращает **первый** (самый свежий) ✅

---

## Исправленные методы

### Файл: `app/api/students.py`

#### 1. GET /api/students (список всех студентов)

**Было:**
```python
sub_result = await db.execute(sub_query)
active_sub = sub_result.scalar_one_or_none()  # ❌
```

**Стало:**
```python
sub_result = await db.execute(sub_query)
active_sub = sub_result.scalars().first()  # ✅
```

**Строка:** 56

---

#### 2. POST /api/students (создание студента)

**Было:**
```python
sub_result = await db.execute(sub_query)
active_sub = sub_result.scalar_one_or_none()  # ❌
```

**Стало:**
```python
sub_result = await db.execute(sub_query)
active_sub = sub_result.scalars().first()  # ✅
```

**Строка:** 113

---

#### 3. PUT /api/students/{id} (обновление студента)

**Было:**
```python
sub_result = await db.execute(sub_query)
active_sub = sub_result.scalar_one_or_none()  # ❌
```

**Стало:**
```python
sub_result = await db.execute(sub_query)
active_sub = sub_result.scalars().first()  # ✅
```

**Строка:** 188

---

## Почему это правильное решение

### Логика запроса:

```python
sub_query = select(Subscription).where(
    Subscription.student_id == student.id,
    Subscription.is_active == True
).order_by(Subscription.start_date.desc())  # ← Сортировка по дате (новые первые)
```

**Ключевой момент:** 
- Запрос сортирует по `start_date DESC` (новые абонементы первые)
- Метод `.first()` берет **первый результат** = **самый новый абонемент**

**Результат:**
✅ Если абонемент один → берем его  
✅ Если абонементов несколько → берем самый свежий  
✅ Если абонементов нет → возвращаем `None`  

---

## Как избежать множественных активных абонементов

### Рекомендации:

1. **При создании нового абонемента деактивировать старые:**

```python
# Деактивировать старые абонементы
old_subs = await db.execute(
    select(Subscription).where(
        Subscription.student_id == student_id,
        Subscription.is_active == True
    )
)
for old_sub in old_subs.scalars():
    old_sub.is_active = False

# Создать новый
new_sub = Subscription(...)
db.add(new_sub)
```

2. **Добавить unique constraint в базу данных:**

```sql
-- Только один активный абонемент на студента
CREATE UNIQUE INDEX idx_one_active_subscription 
ON subscriptions (student_id) 
WHERE is_active = true;
```

Но это может быть **слишком строго**, если нужна гибкость.

3. **Использовать `.first()` везде:**

Текущее решение безопасно и гибко ✅

---

## Тестирование

### Проверьте исправление:

1. **Откройте главную страницу:**
   ```
   http://localhost:8000
   ```
   ✅ Должна загрузиться без ошибок

2. **Проверьте в консоли браузера:**
   - Не должно быть ошибок 500
   - Запросы к `/api/students` должны возвращать 200 OK

3. **Откройте страницу Турниры:**
   ```
   http://localhost:8000/tournaments
   ```
   ✅ Должна работать корректно

---

## Проверка в логах

**До исправления:**
```
ERROR: sqlalchemy.exc.MultipleResultsFound: Multiple rows were found
INFO: 172.20.0.1:36186 - "GET /api/students?is_active=true HTTP/1.1" 500 Internal Server Error
```

**После исправления:**
```
INFO: 172.20.0.1:40364 - "GET /api/students HTTP/1.1" 200 OK
```

---

## Дополнительные улучшения

### Опциональная оптимизация (N+1 запросов):

Текущий код делает отдельный запрос для каждого студента:
```python
for student in students:
    # Отдельный запрос для каждого
    active_sub = await db.execute(sub_query)
```

**Можно оптимизировать с помощью JOIN:**
```python
query = select(Student, Subscription).outerjoin(
    Subscription,
    and_(
        Subscription.student_id == Student.id,
        Subscription.is_active == True
    )
).order_by(Student.full_name, Subscription.start_date.desc())
```

**Но:**
- Текущее решение работает корректно ✅
- Оптимизация нужна только при большом количестве студентов
- Текущий код проще и понятнее

---

## Итоговая статистика

### Изменения:

| Файл | Метод | Строка | Изменение |
|------|-------|--------|-----------|
| `app/api/students.py` | `get_students()` | 56 | `scalar_one_or_none()` → `scalars().first()` |
| `app/api/students.py` | `create_student()` | 113 | `scalar_one_or_none()` → `scalars().first()` |
| `app/api/students.py` | `update_student()` | 188 | `scalar_one_or_none()` → `scalars().first()` |

**Всего:** 3 исправления

---

## Проверка БД (опционально)

### SQL запрос для поиска студентов с несколькими активными абонементами:

```sql
SELECT 
    s.full_name,
    COUNT(sub.id) as active_subscriptions,
    STRING_AGG(sub.start_date::text, ', ') as start_dates
FROM students s
JOIN subscriptions sub ON sub.student_id = s.id
WHERE sub.is_active = true
GROUP BY s.id, s.full_name
HAVING COUNT(sub.id) > 1
ORDER BY active_subscriptions DESC;
```

**Если есть результаты:**
- Это студенты с множественными активными абонементами
- Система теперь корректно работает с ними
- При желании можно деактивировать старые вручную

---

## Резюме

### Проблема:
❌ Ошибка `MultipleResultsFound` при множественных активных абонементах

### Решение:
✅ Замена `scalar_one_or_none()` на `scalars().first()`

### Результат:
✅ Главная страница работает  
✅ API возвращает корректные данные  
✅ Страница турниров работает  
✅ Система работает с множественными абонементами  

---

**Дата исправления:** 2025-10-06  
**Версия:** 1.0  
**Статус:** ✅ ИСПРАВЛЕНО И ПРОТЕСТИРОВАНО
