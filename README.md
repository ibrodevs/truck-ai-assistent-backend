# Truck AI Assistant Backend

Django REST API backend для платформы AI ассистентов для логистики.

## Деплой на Render

### Подготовка

1. Создайте аккаунт на [Render](https://render.com)
2. Подключите ваш GitHub репозиторий

### Настройка базы данных

1. В панели Render создайте новую PostgreSQL базу данных:
   - Тип: PostgreSQL
   - План: Free
   - Имя: truck-ai-db

2. Скопируйте Internal Database URL из настроек БД

### Настройка Web Service

1. Создайте новый Web Service:
   - Тип: Web Service
   - Репозиторий: ваш GitHub репозиторий
   - Название: truck-ai-backend
   - План: Free

2. Настройте переменные окружения:

#### Обязательные переменные:
```
SECRET_KEY=<генерируется автоматически>
DEBUG=false
DATABASE_URL=<URL базы данных из шага выше>
GEMINI_API_KEY=<ваш Gemini API ключ>
CORS_ALLOW_ALL_ORIGINS=false
FRONTEND_URL=https://your-frontend-app.onrender.com
ALLOWED_HOST=your-backend-app.onrender.com
```

3. Настройте команды сборки и запуска:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn truck_platform.wsgi:application`

### Локальная разработка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл .env на основе .env.production:
```bash
cp .env.production .env
```

4. Настройте переменные в .env для локальной разработки

5. Выполните миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер:
```bash
python manage.py runserver
```

## API Endpoints

- `/admin/` - Django админка
- `/api/accounts/` - управление пользователями
- `/api/ai-assistants/` - AI ассистенты
- `/api/notifications/` - уведомления

## Технологии

- Django 6.0.2
- Django REST Framework
- PostgreSQL (продакшен) / SQLite (разработка)
- Gunicorn
- WhiteNoise
- Google Gemini AI