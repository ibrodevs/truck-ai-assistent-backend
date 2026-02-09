from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Create a superuser for production'

    def handle(self, *args, **options):
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('Суперпользователь уже существует')
            )
            return

        # Получаем данные из переменных окружения
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        if not settings.DEBUG:
            # В продакшене проверяем, что пароль установлен
            if password == 'admin123':
                self.stdout.write(
                    self.style.ERROR(
                        'Необходимо установить DJANGO_SUPERUSER_PASSWORD в переменных окружения'
                    )
                )
                return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(f'Суперпользователь "{username}" создан успешно')
        )