# 🚀 Quick Deploy Guide

## Быстрый деплой на Render

### 1. База данных (5 минут)
```
render.com → New + → PostgreSQL
Name: truck-ai-db
Plan: Free
```
📋 **Скопируйте Internal Database URL!**

### 2. Web Service (5 минут)
```
render.com → New + → Web Service
Connect GitHub repo
Name: truck-ai-backend
Build: ./build.sh
Start: gunicorn truck_platform.wsgi:application
```

### 3. Environment Variables
```bash
# Обязательные
SECRET_KEY=<auto>
DEBUG=false
DATABASE_URL=<из шага 1>
GEMINI_API_KEY=AIzaSyCJIWmSSsMTVpv4tAmkOp9PFSW_588rjCE
ALLOWED_HOST=your-app.onrender.com

# CORS (обновите после создания фронтенда)
CORS_ALLOW_ALL_ORIGINS=false
FRONTEND_URL=https://your-frontend.onrender.com

# Админ (опционально)
DJANGO_SUPERUSER_PASSWORD=secure_password_123
```

### 4. Deploy!
Render автоматически запустит деплой. Займет ~10-15 минут.

### 5. Проверка
- Админка: `https://your-app.onrender.com/admin/`
- API: `https://your-app.onrender.com/api/`

---

✅ **Готово!** Backend развернут и готов к работе.

📖 Подробные инструкции: `DEPLOY.md`