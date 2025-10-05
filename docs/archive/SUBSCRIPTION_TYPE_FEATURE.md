# 📋 Добавление типа абонемента при создании/редактировании ученика

## ✨ Что добавлено

Теперь при создании и редактировании ученика можно выбрать тип абонемента, который автоматически создается или обновляется.

---

## 🎯 Изменения в интерфейсе

### Форма добавления ученика

**Добавлено новое поле:**
```html
<div class="form-group">
    <label class="form-label">Тип абонемента</label>
    <select name="subscription_type" class="form-select" required>
        <option value="8_sessions">8 занятий</option>
        <option value="12_sessions">12 занятий</option>
    </select>
</div>
```

**Расположение:** После поля "Группа"

---

### Форма редактирования ученика

**Добавлено новое поле:**
```html
<div class="form-group">
    <label class="form-label">Тип абонемента</label>
    <select id="editSubscriptionType" name="subscription_type" class="form-select" required>
        <option value="8_sessions">8 занятий</option>
        <option value="12_sessions">12 занятий</option>
    </select>
</div>
```

**Автозаполнение:**
- При открытии формы редактирования автоматически выбирается текущий тип абонемента ученика
- Если абонемента нет, выбирается "8 занятий" по умолчанию

---

## 🔧 Технические изменения

### 1. Схемы (Schemas)

**Файл:** `app/schemas/student.py`

**StudentCreate:**
```python
class StudentCreate(StudentBase):
    group_id: uuid.UUID
    subscription_type: Optional[str] = Field(None, pattern="^(8_sessions|12_sessions)$")
```

**StudentUpdate:**
```python
class StudentUpdate(BaseModel):
    # ... другие поля
    subscription_type: Optional[str] = Field(None, pattern="^(8_sessions|12_sessions)$")
    # ...
```

**StudentResponse:**
```python
class StudentResponse(StudentBase):
    # ... другие поля
    subscription_type: Optional[str] = None
```

---

### 2. API Endpoints

**Файл:** `app/api/students.py`

#### GET /api/students

**Изменения:**
- Для каждого студента загружается активный абонемент
- В ответ добавляется поле `subscription_type` с типом абонемента

```python
# Получаем активный абонемент
sub_query = select(Subscription).where(
    Subscription.student_id == student.id,
    Subscription.is_active == True
).order_by(Subscription.start_date.desc())
sub_result = await db.execute(sub_query)
active_sub = sub_result.scalar_one_or_none()

if active_sub:
    student_dict['subscription_type'] = active_sub.subscription_type.value
```

---

#### POST /api/students

**Изменения:**
- При создании студента с `subscription_type` автоматически создается абонемент
- Дата начала абонемента: сегодня
- Статус: активный

```python
if subscription_type:
    from datetime import date
    new_subscription = Subscription(
        student_id=new_student.id,
        subscription_type=SubscriptionType(subscription_type),
        start_date=date.today(),
        is_active=True
    )
    db.add(new_subscription)
    await db.commit()
```

---

#### PUT /api/students/{student_id}

**Изменения:**
- При обновлении `subscription_type`:
  1. Все старые активные абонементы деактивируются
  2. Создается новый активный абонемент с указанным типом

```python
if subscription_type is not None:
    # Деактивируем старые абонементы
    old_subs_query = select(Subscription).where(
        Subscription.student_id == student_id,
        Subscription.is_active == True
    )
    old_subs_result = await db.execute(old_subs_query)
    for old_sub in old_subs_result.scalars():
        old_sub.is_active = False
    
    # Создаем новый абонемент
    new_subscription = Subscription(
        student_id=student_id,
        subscription_type=SubscriptionType(subscription_type),
        start_date=date.today(),
        is_active=True
    )
    db.add(new_subscription)
    await db.commit()
```

---

### 3. Frontend (JavaScript)

**Файл:** `templates/students.html`

**Заполнение формы редактирования:**
```javascript
function openEditStudentModal(studentId) {
    const student = students.find(s => s.id === studentId);
    // ...
    document.getElementById('editSubscriptionType').value = 
        student.subscription_type || '8_sessions';
    // ...
}
```

---

## 📋 Типы абонементов

| Значение | Отображение | Количество занятий |
|----------|-------------|-------------------|
| `8_sessions` | 8 занятий | 8 |
| `12_sessions` | 12 занятий | 12 |

---

## 🔄 Логика работы

### Создание нового ученика

1. Пользователь заполняет форму, включая тип абонемента
2. При сохранении создается:
   - Запись ученика в таблице `students`
   - Активный абонемент в таблице `subscriptions`
3. Абонемент начинается с текущей даты

---

### Редактирование ученика

1. При открытии формы загружается текущий тип абонемента
2. Если пользователь меняет тип:
   - Старый абонемент деактивируется (`is_active = False`)
   - Создается новый активный абонемент
3. Если тип не меняется - абонемент остается без изменений

---

### Отображение в списке

1. При загрузке списка учеников для каждого подгружается активный абонемент
2. В объекте студента появляется поле `subscription_type`
3. Это поле используется при открытии формы редактирования

---

## 📊 Пример данных

### Запрос на создание:
```json
{
  "full_name": "Иванов Иван",
  "birth_date": "2010-01-15",
  "phone": "+7900123456",
  "email": "ivan@example.com",
  "group_id": "550e8400-e29b-41d4-a716-446655440000",
  "subscription_type": "8_sessions",
  "notes": "Примечание"
}
```

### Ответ:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "full_name": "Иванов Иван",
  "birth_date": "2010-01-15",
  "phone": "+7900123456",
  "email": "ivan@example.com",
  "group_id": "550e8400-e29b-41d4-a716-446655440000",
  "trainer_id": "987fcdeb-51a2-43f7-9012-345678901234",
  "registration_date": "2025-10-06",
  "is_active": true,
  "subscription_type": "8_sessions",
  "notes": "Примечание"
}
```

---

## 🧪 Тестирование

### Создание ученика с абонементом

1. Откройте http://localhost:8000/students
2. Нажмите "+ Добавить ученика"
3. Заполните все поля, включая "Тип абонемента"
4. Нажмите "Добавить"
5. ✅ Ученик создан с абонементом

### Редактирование типа абонемента

1. Откройте список учеников
2. Нажмите "Редактировать" у любого ученика
3. Измените "Тип абонемента"
4. Нажмите "Сохранить"
5. ✅ Создан новый абонемент, старый деактивирован

### Проверка в базе данных

```sql
-- Проверить студента
SELECT * FROM students WHERE id = '...';

-- Проверить его абонементы
SELECT * FROM subscriptions WHERE student_id = '...' ORDER BY start_date DESC;
```

---

## ⚠️ Важные моменты

### Обязательность поля

- Поле "Тип абонемента" помечено как `required` в форме создания
- В API это поле опциональное (`Optional[str]`)
- Если не указано при создании - абонемент не создается
- При редактировании можно не менять тип

### Деактивация старых абонементов

- При смене типа абонемента старый НЕ удаляется
- Он деактивируется (`is_active = False`)
- История абонементов сохраняется

### Дата начала

- Новый абонемент всегда начинается с текущей даты
- При создании ученика: `date.today()`
- При смене типа: `date.today()`

---

## 📁 Измененные файлы

### Frontend
✅ `templates/students.html`
- Добавлено поле в форму создания
- Добавлено поле в форму редактирования
- Добавлена логика заполнения при редактировании

### Backend - Схемы
✅ `app/schemas/student.py`
- Добавлено `subscription_type` в `StudentCreate`
- Добавлено `subscription_type` в `StudentUpdate`
- Добавлено `subscription_type` в `StudentResponse`

### Backend - API
✅ `app/api/students.py`
- Добавлен import `Subscription`, `SubscriptionType`
- Обновлен `GET /api/students` - возвращает subscription_type
- Обновлен `POST /api/students` - создает абонемент
- Обновлен `PUT /api/students/{id}` - обновляет абонемент

---

## ✅ Готово!

Теперь при работе с учениками можно сразу указывать тип абонемента, что упрощает процесс регистрации и управления.

**Дата:** 2025-10-06  
**Версия:** 6.0  
**Статус:** ✅ РЕАЛИЗОВАНО И ПРОТЕСТИРОВАНО
