# Инструкции по деплою на Render

## Шаг 1: Подготовка репозитория

1. Убедитесь, что все изменения закоммичены и запушены в GitHub
2. Файлы для деплоя созданы:
   - `build.sh` - скрипт сборки
   - `render.yaml` - конфигурация Render
   - `requirements.txt` - зависимости Python
   - `runtime.txt` - версия Python
   - `.gitignore` - игнорируемые файлы

## Шаг 2: Создание базы данных

1. Зайдите на [render.com](https://render.com) и войдите в аккаунт
2. Нажмите "New +" → "PostgreSQL"
3. Настройки:
   - Name: `truck-ai-db`
   - Plan: Free
   - Region: выберите ближайший к вашим пользователям
4. Нажмите "Create Database"
5. **ВАЖНО**: Скопируйте "Internal Database URL" - он понадобится для веб-сервиса

## Шаг 3: Создание веб-сервиса

1. Нажмите "New +" → "Web Service"
2. Подключите GitHub репозиторий с проектом
3. Настройки:
   - Name: `truck-ai-backend`
   - Region: тот же, что и для БД
   - Branch: `main`
   - Runtime: Python 3
   - Build Command: `./build.sh`
   - Start Command: `gunicorn truck_platform.wsgi:application`
   - Plan: Free

## Шаг 4: Настройка переменных окружения

В разделе "Environment Variables" добавьте:

### Обязательные переменные:

```
SECRET_KEY = <автогенерируется Render>
DEBUG = false
DATABASE_URL = <Internal Database URL из шага 2>
GEMINI_API_KEY = <ваш API ключ Google Gemini>
CORS_ALLOW_ALL_ORIGINS = false
FRONTEND_URL = https://your-frontend.onrender.com
ALLOWED_HOST = your-backend-app.onrender.com
```

### Опциональные переменные для суперпользователя:

```
DJANGO_SUPERUSER_USERNAME = admin
DJANGO_SUPERUSER_EMAIL = admin@truckai.com
DJANGO_SUPERUSER_PASSWORD = <надежный пароль>
```

## Шаг 5: Деплой

1. Нажмите "Create Web Service"
2. Render автоматически запустит процесс деплоя
3. Следите за логами в разделе "Events"
4. После успешного деплоя сервис будет доступен по URL вида: `https://your-app-name.onrender.com`

## Шаг 6: Проверка

1. Откройте `https://your-app-name.onrender.com/admin/`
2. Войдите с учетными данными суперпользователя
3. Проверьте, что API доступно: `https://your-app-name.onrender.com/api/`

## Важные заметки

- **Первый деплой** может занять 10-15 минут
- **Free план Render** "засыпает" через 15 минут неактивности
- **База данных** на free плане автоматически удаляется через 90 дней
- **URL вашего приложения**: обновите FRONTEND_URL и ALLOWED_HOST после создания

## Обновление приложения

1. Сделайте изменения в коде
2. Закоммитьте и запушьте в GitHub
3. Render автоматически перезапустит деплой при изменениях в main ветке

## Настройка домена (опционально)

1. В настройках веб-сервиса перейдите в "Settings"
2. В разделе "Custom Domains" добавьте ваш домен
3. Обновите переменную ALLOWED_HOST

## Мониторинг и логи

- **Логи**: вкладка "Logs" в панели управления сервисом
- **Метрики**: вкладка "Metrics" для отслеживания производительности
- **Health checks**: автоматически проверяют `/admin/` endpoint

## Troubleshooting

### Ошибка "Build failed"
- Проверьте `build.sh` на права выполнения
- Убедитесь, что все зависимости в `requirements.txt`

### Ошибка "Application failed to start"
- Проверьте переменные окружения
- Посмотрите логи для подробностей

### Ошибки базы данных
- Убедитесь, что DATABASE_URL корректный
- Проверьте, что БД создана и доступна