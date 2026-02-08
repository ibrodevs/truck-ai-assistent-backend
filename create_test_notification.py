"""
Скрипт для создания тестового уведомления через Django Shell
Запустить: python manage.py shell < create_test_notification.py
"""

from accounts.models import UserProfile
from notifications.models import Notification

# Получаем всех пользователей
users = UserProfile.objects.all()

if users.exists():
    for user in users:
        # Создаем тестовое уведомление для каждого пользователя
        notification = Notification.objects.create(
            recipient=user,
            title='🔔 Тестовое push-уведомление',
            message='Система push-уведомлений работает! Вы будете получать важные обновления в реальном времени.',
            notification_type='system',
            link='/notifications'
        )
        print(f'Создано уведомление для {user.user.username}: {notification.title}')
else:
    print('Нет пользователей в системе')
