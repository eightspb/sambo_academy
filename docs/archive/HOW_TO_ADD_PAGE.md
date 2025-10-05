# 🚀 Как добавить новую страницу

## Быстрый старт

### 1. Создайте HTML файл

Скопируйте `templates/base.html` или используйте шаблон:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Моя страница - Sambo Academy</title>
    <link rel="manifest" href="/static/manifest.json">
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <!-- Header Component -->
    <div id="app-header"></div>
    
    <!-- Navigation Component -->
    <div id="app-nav"></div>
    
    <!-- Ваш контент -->
    <main class="container">
        <h1>Заголовок</h1>
        <p>Контент...</p>
    </main>
    
    <!-- Скрипты -->
    <script src="/static/js/components.js"></script>
    <script src="/static/js/app.js"></script>
    <script>
        // Ваш JavaScript
        async function loadData() {
            await auth.checkAuth();
            // ...
        }
        loadData();
    </script>
</body>
</html>
```

### 2. Добавьте route в backend

**File:** `app/main.py`

```python
@app.get("/mypage")
async def mypage():
    """Serve my page."""
    return FileResponse("templates/mypage.html")
```

### 3. Добавьте ссылку в навигацию (опционально)

**File:** `templates/components/nav.html`

```html
<li class="nav-item">
    <a href="/mypage" class="nav-link">📄 Моя страница</a>
</li>
```

✅ **Готово!** Страница доступна по адресу http://localhost:8000/mypage

---

## Что включено автоматически

✅ Header с логотипом и кнопкой выхода  
✅ Навигационное меню  
✅ Подсветка текущей страницы  
✅ Адаптивный дизайн  
✅ PWA возможности  

---

## Важно

**Обязательные элементы:**
1. `<div id="app-header"></div>` - для header
2. `<div id="app-nav"></div>` - для навигации  
3. `<script src="/static/js/components.js"></script>` - загрузчик компонентов
4. `<script src="/static/js/app.js"></script>` - общие функции

**Порядок скриптов:**
```html
<script src="/static/js/components.js"></script> <!-- 1. Компоненты -->
<script src="/static/js/app.js"></script>        <!-- 2. API/Auth -->
<script>/* Ваш код */</script>                   <!-- 3. Страничный код -->
```

---

## Примеры

### Страница со списком

```html
<main class="container">
    <h1>Список</h1>
    <div id="itemsList"></div>
</main>

<script>
async function loadData() {
    await auth.checkAuth();
    const items = await api.get('/api/items');
    document.getElementById('itemsList').innerHTML = items.map(item => `
        <div class="card">${item.name}</div>
    `).join('');
}
loadData();
</script>
```

### Страница с формой

```html
<main class="container">
    <h1>Создать</h1>
    <form id="myForm" onsubmit="handleSubmit(event)">
        <input type="text" name="name" class="form-input">
        <button type="submit" class="btn btn-primary">Сохранить</button>
    </form>
</main>

<script>
async function handleSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    await api.post('/api/items', Object.fromEntries(formData));
    ui.showSuccess('Сохранено!');
}
</script>
```

---

## Готовые стили

Используйте классы из `static/css/styles.css`:

- `.card` - карточка
- `.btn btn-primary` - основная кнопка
- `.form-input` - поле ввода
- `.grid grid-2` - сетка 2 колонки
- `.badge badge-success` - бейдж

---

**Подробнее:** См. `docs/SHARED_COMPONENTS.md`
