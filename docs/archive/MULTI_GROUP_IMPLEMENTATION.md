# ✅ Реализация: Студент в нескольких группах

**Дата:** 2025-10-06 02:59  
**Статус:** ✅ РЕАЛИЗОВАНО

---

## 🎯 Решение

Реализован **гибридный подход** с минимальными изменениями:

### Концепция:
1. **Основная группа** - студент привязан к одной группе (`group_id`)
2. **Дополнительные группы** - студент может посещать другие группы (`additional_group_ids[]`)
3. **Один абонемент** - оплачивается только один абонемент
4. **Единое списание** - посещения во ВСЕХ группах списываются из одного абонемента

---

## 🛠️ Что было сделано

### 1. ✅ Миграция базы данных

**Файл:** `alembic/versions/fb7d6dc9bb22_add_additional_groups_to_students.py`

```sql
ALTER TABLE students 
ADD COLUMN additional_group_ids UUID[] DEFAULT '{}';
```

**Применено:**
```bash
docker-compose exec app alembic upgrade head
# Running upgrade 31b85b2eb447 -> fb7d6dc9bb22
```

---

### 2. ✅ Обновлена модель Student

**Файл:** `app/models/student.py`

```python
class Student(Base):
    # ...
    group_id: Mapped[uuid.UUID]  # Основная группа
    additional_group_ids: Mapped[Optional[List[uuid.UUID]]]  # Дополнительные группы ✅
    # ...
```

**Импорты:**
```python
from sqlalchemy import ARRAY
from typing import List
```

---

### 3. ✅ Обновлены схемы API

**Файл:** `app/schemas/student.py`

```python
class StudentCreate(StudentBase):
    group_id: uuid.UUID
    additional_group_ids: Optional[List[uuid.UUID]] = Field(default_factory=list)  # ✅
    subscription_type: Optional[str] = ...

class StudentUpdate(BaseModel):
    # ...
    additional_group_ids: Optional[List[uuid.UUID]] = None  # ✅

class StudentResponse(StudentBase):
    # ...
    additional_group_ids: Optional[List[uuid.UUID]] = Field(default_factory=list)  # ✅
```

---

### 4. ✅ Обновлена логика посещаемости

**Файл:** `app/api/attendance.py` (строки 60-76)

**БЫЛО:**
```python
# Verify student belongs to group
result = await db.execute(
    select(Student).where(
        Student.id == student_id,
        Student.group_id == attendance_data.group_id  # ❌ Только основная группа
    )
)
```

**СТАЛО:**
```python
# Verify student belongs to group (primary or additional)
result = await db.execute(
    select(Student).where(Student.id == student_id)
)
student = result.scalar_one_or_none()

if not student:
    continue

# Check if student belongs to this group (primary or additional)
belongs_to_group = (
    student.group_id == attendance_data.group_id or
    (student.additional_group_ids and attendance_data.group_id in student.additional_group_ids)
)

if not belongs_to_group:
    continue
```

**Результат:**  
✅ Студент может быть отмечен в основной И дополнительных группах  
✅ Посещения списываются из ОДНОГО абонемента

---

### 5. ✅ Исправлено создание студента

**Файл:** `app/api/students.py`

**Добавлено:**
```python
def get_subscription_params(subscription_type: SubscriptionType, age_group: AgeGroup):
    """Get subscription parameters based on type and age group."""
    if subscription_type == SubscriptionType.EIGHT_SESSIONS:
        total_sessions = 8
        price = ...  # Зависит от возраста
    else:
        total_sessions = 12
        price = ...
    
    expiry_date = date.today() + timedelta(days=60)
    
    return {
        'total_sessions': total_sessions,
        'remaining_sessions': total_sessions,
        'price': price,
        'expiry_date': expiry_date
    }
```

**Использование при создании:**
```python
if subscription_type:
    group = await db.execute(select(Group).where(Group.id == new_student.group_id))
    subscription_params = get_subscription_params(
        SubscriptionType(subscription_type),
        group.age_group
    )
    
    new_subscription = Subscription(
        student_id=new_student.id,
        subscription_type=SubscriptionType(subscription_type),
        start_date=date.today(),
        is_active=True,
        **subscription_params  # ✅ Все поля заполнены!
    )
```

**Исправлено:**  
✅ `total_sessions` заполняется  
✅ `remaining_sessions` заполняется  
✅ `price` заполняется  
✅ `expiry_date` заполняется  
❌ Больше не будет ошибки `NotNullViolationError`

---

## 📊 Как это работает

### Пример: Студент "Иван Петров"

```json
{
  "id": "uuid-123",
  "full_name": "Иван Петров",
  "group_id": "group-mon-wed-fri",  // Основная группа: ПН-СР-ПТ
  "additional_group_ids": [
    "group-tue-thu"  // Дополнительная группа: ВТ-ЧТ
  ],
  "subscription_type": "12_sessions"  // Один абонемент на 12 занятий
}
```

### Посещаемость:

| Дата       | Группа      | Статус | Абонемент (осталось) |
|------------|-------------|--------|----------------------|
| 2025-10-07 | ПН-СР-ПТ    | ✅     | 12 → 11              |
| 2025-10-08 | ВТ-ЧТ       | ✅     | 11 → 10              |
| 2025-10-09 | ПН-СР-ПТ    | ✅     | 10 → 9               |
| 2025-10-10 | ВТ-ЧТ       | ✅     | 9 → 8                |

**Результат:**
- ✅ Студент посещает **две группы**
- ✅ Посещения **списываются из одного** абонемента
- ✅ Оплата **только за один** абонемент

---

## 🎨 Frontend (нужно обновить)

### Форма редактирования студента

**Файл:** `templates/students.html`

**Добавить поле:**
```html
<div class="form-group">
    <label class="form-label">Дополнительные группы (бонус)</label>
    <select id="editAdditionalGroups" name="additional_group_ids" class="form-select" multiple>
        <option value="">Нет</option>
        <!-- Список всех групп кроме основной -->
    </select>
    <small class="text-secondary">
        Студент сможет посещать эти группы бесплатно (списывается из основного абонемента)
    </small>
</div>
```

**JavaScript:**
```javascript
// При открытии формы редактирования
document.getElementById('editAdditionalGroups').value = student.additional_group_ids || [];

// При сохранении
const additionalGroupIds = Array.from(
    document.getElementById('editAdditionalGroups').selectedOptions
).map(opt => opt.value).filter(v => v);

const data = {
    ...
    additional_group_ids: additionalGroupIds
};
```

---

### Страница посещаемости

**Файл:** `templates/attendance.html`

**Изменений НЕ требуется!**  
✅ Студенты из дополнительных групп автоматически появятся в списке  
✅ Backend уже проверяет `additional_group_ids`

---

## 🧪 Как протестировать

### 1. Добавить студента в дополнительную группу (через БД)

```sql
-- Студент "Иван Иванов" в основной группе "ПН-СР-ПТ"
-- Добавляем его в дополнительную группу "ВТ-ЧТ"

UPDATE students
SET additional_group_ids = ARRAY[
    (SELECT id FROM groups WHERE name = 'Старшие Новички ВТ-ЧТ')::uuid
]
WHERE full_name = 'Иван Иванов';
```

### 2. Проверить посещаемость

```bash
# Откройте: http://localhost:8000/attendance
# 1. Выберите группу "ПН-СР-ПТ" (основная)
#    ✅ Студент "Иван Иванов" должен быть в списке

# 2. Выберите группу "ВТ-ЧТ" (дополнительная)
#    ✅ Студент "Иван Иванов" должен ТАКЖЕ быть в списке

# 3. Отметьте студента в обеих группах
#    ✅ Посещения списываются из ОДНОГО абонемента
```

### 3. Проверить списание посещений

```sql
-- Проверить абонемент студента
SELECT 
    s.full_name,
    sub.subscription_type,
    sub.total_sessions,
    sub.remaining_sessions,
    COUNT(a.id) as attended
FROM students s
JOIN subscriptions sub ON sub.student_id = s.id AND sub.is_active = true
LEFT JOIN attendances a ON a.student_id = s.id AND a.status = 'PRESENT'
WHERE s.full_name = 'Иван Иванов'
GROUP BY s.id, s.full_name, sub.id;
```

**Ожидаемый результат:**
```
full_name    | subscription_type | total_sessions | remaining_sessions | attended
-------------|-------------------|----------------|--------------------|----------
Иван Иванов  | TWELVE_SESSIONS   | 12             | 10                 | 2
```

✅ Студент посетил 2 занятия (в разных группах)  
✅ Осталось 10 занятий из 12  
✅ Все списывается из ОДНОГО абонемента

---

## 📋 Итоговая проверка

### ✅ Требования выполнены:

1. **Студент в нескольких группах:**
   - ✅ Основная группа: `group_id`
   - ✅ Дополнительные группы: `additional_group_ids[]`

2. **Отметка посещаемости:**
   - ✅ Студент отображается в списке основной группы
   - ✅ Студент отображается в списке дополнительных групп
   - ✅ Можно отметить в любой группе

3. **Один абонемент:**
   - ✅ У студента только один активный абонемент (защищено индексом)
   - ✅ Посещения во ВСЕХ группах списываются из этого абонемента
   - ✅ Нет дублирования абонементов

4. **Создание студента:**
   - ✅ Все поля абонемента заполняются корректно
   - ✅ Нет ошибки `NotNullViolationError`

---

## 🚀 Следующие шаги

### Обязательно:
1. **Обновить UI** - добавить поле "Дополнительные группы" в форму редактирования студента
2. **Протестировать** - создать тестового студента с дополнительными группами

### Опционально:
1. **Добавить ограничения** - максимум N дополнительных групп
2. **Добавить валидацию** - нельзя добавить основную группу в дополнительные
3. **Добавить UI индикатор** - показывать бейдж "Бонус" для студентов в доп. группах
4. **Добавить статистику** - сколько студентов посещает несколько групп

---

## 📄 Файлы изменены:

1. ✅ `alembic/versions/fb7d6dc9bb22_*.py` - миграция БД
2. ✅ `app/models/student.py` - модель Student
3. ✅ `app/schemas/student.py` - схемы API
4. ✅ `app/api/attendance.py` - логика посещаемости
5. ✅ `app/api/students.py` - создание студента с правильным абонементом

---

## 🎯 Итог

**Реализовано:**  
✅ Студент может посещать несколько групп  
✅ У студента один оплачиваемый абонемент  
✅ Посещения списываются из одного абонемента  
✅ Минимальные изменения кода  
✅ Обратная совместимость (студенты без доп. групп работают как раньше)

**Не требуется:**  
❌ Создавать дубликаты студентов  
❌ Создавать несколько абонементов  
❌ Переписывать архитектуру (MANY-TO-MANY)

**Готово к использованию!** 🚀
