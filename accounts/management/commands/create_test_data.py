from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from notifications.models import Notification
from ai_assistants.models import Conversation, Message


class Command(BaseCommand):
    help = 'Create test data for demo purposes'

    def handle(self, *args, **options):
        # Создаем тестового пользователя
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Тест',
                'last_name': 'Пользователь'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Создан тестовый пользователь: {test_user.username}')
            )
        
        # Создаем или обновляем профиль
        profile, profile_created = UserProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'role': 'trucker',
                'phone': '+7900000000',
                'bio': 'Тестовый пользователь для демо'
            }
        )
        
        if profile_created:
            self.stdout.write(
                self.style.SUCCESS(f'Создан профиль для пользователя: {test_user.username}')
            )
        
        # Создаем тестовые уведомления
        notifications_count = Notification.objects.filter(recipient=profile).count()
        if notifications_count == 0:
            # Создаем несколько тестовых уведомлений
            notifications = [
                {
                    'title': 'Добро пожаловать!',
                    'message': 'Добро пожаловать в систему TruckAI. Здесь вы можете общаться с ИИ ассистентами.',
                    'notification_type': 'info'
                },
                {
                    'title': 'Новый заказ',
                    'message': 'Поступил новый заказ на маршрут Москва-СПб. Проверьте детали в личном кабинете.',
                    'notification_type': 'order'
                },
                {
                    'title': 'Напоминание',
                    'message': 'Не забудьте обновить данные о техническом состоянии транспорта.',
                    'notification_type': 'reminder'
                }
            ]
            
            for notif_data in notifications:
                Notification.objects.create(
                    recipient=profile,
                    **notif_data
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Создано {len(notifications)} тестовых уведомлений')
            )
        
        # Создаем тестовые диалоги
        conversations_count = Conversation.objects.filter(user=test_user).count()
        if conversations_count == 0:
            # Создаем тестовый диалог с ИИ
            conversation = Conversation.objects.create(
                user=test_user,
                assistant_type='general',
                title='Знакомство с системой'
            )
            
            # Добавляем несколько сообщений
            Message.objects.create(
                conversation=conversation,
                content='Привет! Как дела с доставкой?',
                is_user_message=True
            )
            
            Message.objects.create(
                conversation=conversation,
                content='Привет! Я ваш ИИ-ассистент TruckAI. Готов помочь с вопросами по логистике, маршрутам и документообороту. Что вас интересует?',
                is_user_message=False
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Создан тестовый диалог: {conversation.title}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Тестовые данные успешно созданы!')
        )