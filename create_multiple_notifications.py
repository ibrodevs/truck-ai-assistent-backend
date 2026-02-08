"""
Скрипт для создания различных типов уведомлений
"""

from accounts.models import UserProfile
from notifications.models import Notification

# Получаем всех пользователей
users = UserProfile.objects.all()

if users.exists():
    for user in users:
        # Уведомление о новом совпадении водителя
        Notification.objects.create(
            recipient=user,
            title='🚛 Найден подходящий водитель',
            message=f'Для маршрута Москва-Казань найден водитель с рейтингом 4.9. Посмотрите профиль и свяжитесь.',
            notification_type='match',
            link='/driver-matching'
        )
        
        # Уведомление о новом сообщении
        Notification.objects.create(
            recipient=user,
            title='💬 Новое сообщение',
            message='У вас есть непрочитанное сообщение от AI-ассистента по маршрутам.',
            notification_type='message',
            link='/history'
        )
        
        # Уведомление о новой оценке
        Notification.objects.create(
            recipient=user,
            title='⭐ Новая оценка',
            message='Диспетчер оценил вашу работу на 5 звезд. Отличная работа!',
            notification_type='rating',
            link='/settings'
        )
        
        print(f'✅ Создано 3 уведомления для {user.user.username}')
else:
    print('❌ Нет пользователей в системе')

print(f'\n📊 Всего уведомлений в системе: {Notification.objects.count()}')
