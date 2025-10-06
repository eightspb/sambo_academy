# 🧪 Руководство по тестированию

## ❌ Исправленная ошибка

### Проблема:
На странице статистики при загрузке вкладки "Посещаемость" возникала ошибка:
```
NameError: name 'func' is not defined
```

### Причина:
В файле `/app/api/attendance.py` не был импортирован `func` из SQLAlchemy, который используется для агрегирующих функций (COUNT, SUM и т.д.).

### Решение:
Добавлен импорт:
```python
from sqlalchemy import select, func  # ← добавлен func
```

### Проверка исправления:
✅ Приложение перезапущено
✅ Endpoint `/api/attendance/statistics/summary` работает корректно

---

## 🧪 Созданные тесты

### Структура тестов:

```
tests/
├── __init__.py
├── conftest.py          # Фикстуры и конфигурация
└── test_statistics.py   # Тесты статистики
```

### Покрытие:

#### 1. **Тесты статистики посещаемости** (`TestAttendanceStatistics`)
- ✅ `test_get_attendance_statistics_success` - успешное получение статистики
- ✅ `test_get_attendance_statistics_default_params` - параметры по умолчанию
- ✅ `test_get_attendance_statistics_group_structure` - структура данных по группам

#### 2. **Тесты статистики платежей** (`TestPaymentStatistics`)
- ✅ `test_get_payment_statistics_success` - успешное получение статистики
- ✅ `test_get_payment_statistics_default_year` - год по умолчанию

#### 3. **Тесты неоплативших учеников** (`TestUnpaidStudents`)
- ✅ `test_get_unpaid_students_success` - успешное получение списка
- ✅ `test_get_unpaid_students_structure` - структура данных
- ✅ `test_get_unpaid_students_default_params` - параметры по умолчанию
- ✅ `test_get_unpaid_students_unauthorized` - проверка авторизации

#### 4. **Тесты защиты от дублирования турниров** (`TestTournamentDuplicatePrevention`)
- ✅ `test_add_duplicate_participant_fails` - предотвращение дублей
- ✅ `test_update_participant_success` - обновление участника
- ✅ `test_delete_participant_success` - удаление участника

---

## 🚀 Запуск тестов

### Предварительные требования:

Установите зависимости для тестирования:
```bash
pip install pytest pytest-asyncio httpx
```

### Команды запуска:

**1. Запустить все тесты:**
```bash
docker-compose exec app pytest
```

**2. Запустить с подробным выводом:**
```bash
docker-compose exec app pytest -v
```

**3. Запустить конкретный файл:**
```bash
docker-compose exec app pytest tests/test_statistics.py
```

**4. Запустить конкретный тест:**
```bash
docker-compose exec app pytest tests/test_statistics.py::TestAttendanceStatistics::test_get_attendance_statistics_success
```

**5. Запустить с покрытием кода:**
```bash
docker-compose exec app pytest --cov=app --cov-report=html
```

**6. Запустить только быстрые тесты:**
```bash
docker-compose exec app pytest -m "not slow"
```

---

## 📊 Что проверяют тесты

### Проверка структуры ответа:

```python
# Пример теста статистики посещаемости
def test_get_attendance_statistics_success():
    response = await client.get("/api/attendance/statistics/summary?year=2025&month=10")
    
    assert response.status_code == 200
    data = response.json()
    
    # Проверка наличия всех полей
    assert "year" in data
    assert "month" in data
    assert "groups" in data
    assert "overall" in data
    
    # Проверка типов
    assert isinstance(data["groups"], list)
    assert isinstance(data["overall"]["total_sessions"], int)
    
    # Проверка диапазонов значений
    assert 0 <= data["overall"]["attendance_rate"] <= 100
```

### Проверка бизнес-логики:

```python
# Пример теста защиты от дублирования
def test_add_duplicate_participant_fails():
    # Добавляем участника первый раз - должно пройти
    response1 = await client.post("/api/tournaments/{id}/participants", json=data)
    assert response1.status_code == 201
    
    # Пытаемся добавить снова - должно упасть
    response2 = await client.post("/api/tournaments/{id}/participants", json=data)
    assert response2.status_code == 400
    assert "уже добавлен" in response2.json()["detail"]
```

---

## 🔧 Фикстуры (fixtures)

### Базовые фикстуры:

**`client`** - HTTP клиент для тестирования API
```python
async def test_example(client: AsyncClient):
    response = await client.get("/api/endpoint")
```

**`auth_headers`** - заголовки с токеном авторизации
```python
async def test_example(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/endpoint", headers=auth_headers)
```

**`db_session`** - сессия тестовой БД
```python
async def test_example(db_session: AsyncSession):
    user = User(...)
    db_session.add(user)
    await db_session.commit()
```

### Фикстуры тестовых данных:

- **`test_user`** - тестовый пользователь
- **`test_group`** - тестовая группа
- **`test_student`** - тестовый ученик
- **`test_tournament`** - тестовый турнир
- **`test_participation`** - тестовое участие в турнире

---

## 📝 Написание новых тестов

### Шаблон теста:

```python
import pytest
from httpx import AsyncClient


class TestMyFeature:
    """Tests for my new feature."""
    
    @pytest.mark.asyncio
    async def test_feature_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful scenario."""
        # Arrange (подготовка)
        data = {"key": "value"}
        
        # Act (действие)
        response = await client.post("/api/endpoint", json=data, headers=auth_headers)
        
        # Assert (проверка)
        assert response.status_code == 201
        result = response.json()
        assert result["key"] == "value"
    
    @pytest.mark.asyncio
    async def test_feature_validation_error(self, client: AsyncClient, auth_headers: dict):
        """Test validation error."""
        # Невалидные данные
        data = {"key": ""}
        
        response = await client.post("/api/endpoint", json=data, headers=auth_headers)
        
        # Должна быть ошибка валидации
        assert response.status_code == 422
```

---

## ✅ Чек-лист перед коммитом

Перед отправкой кода проверьте:

- [ ] Все тесты проходят (`pytest`)
- [ ] Нет падающих тестов
- [ ] Покрытие кода не уменьшилось
- [ ] Новый код покрыт тестами
- [ ] Тесты документированы (docstrings)
- [ ] Нет хардкода в тестах
- [ ] Используются фикстуры для тестовых данных

---

## 🐛 Отладка тестов

### Запустить тесты в режиме отладки:

```bash
docker-compose exec app pytest -vv --pdb
```

### Показать print() вывод:

```bash
docker-compose exec app pytest -s
```

### Запустить только упавшие тесты:

```bash
docker-compose exec app pytest --lf
```

### Остановиться на первой ошибке:

```bash
docker-compose exec app pytest -x
```

---

## 📈 Метрики покрытия

### Генерация отчета:

```bash
docker-compose exec app pytest --cov=app --cov-report=html
```

### Просмотр отчета:

Откройте `htmlcov/index.html` в браузере.

### Цели покрытия:

- **Минимум**: 70% покрытия кода
- **Цель**: 85% покрытия кода
- **Критичные модули**: 95% покрытия (API endpoints, бизнес-логика)

---

## 🚨 Устранение неполадок

### Проблема: Тесты не находят модули

**Решение:** Проверьте PYTHONPATH
```bash
export PYTHONPATH=/app:$PYTHONPATH
```

### Проблема: База данных уже существует

**Решение:** Пересоздайте тестовую БД
```bash
docker-compose exec db psql -U sambo_user -c "DROP DATABASE IF EXISTS sambo_test;"
docker-compose exec db psql -U sambo_user -c "CREATE DATABASE sambo_test;"
```

### Проблема: Медленные тесты

**Решение:** Используйте транзакции вместо фикстур с сессиями
```python
@pytest.fixture
async def db_session(test_engine):
    async with async_session() as session:
        yield session
        await session.rollback()  # Откатываем изменения
```

---

## 📚 Полезные ресурсы

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Asyncio](https://pytest-asyncio.readthedocs.io/)
- [HTTPX Documentation](https://www.python-httpx.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Теперь все изменения проверяются автоматическими тестами! ✅**
