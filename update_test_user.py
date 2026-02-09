#!/usr/bin/env python

import os
import sys
import django

# Добавляем путь к проекту
sys.path.append('/Users/imac5/Desktop/98hgfd/truck/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'truck_platform.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def update_test_user_role():
    """Обновляет роль тестового пользователя на диспетчера"""
    
    try:
        # Находим тестового пользователя
        test_user = User.objects.get(username='test_user')
        print(f"✅ Найден пользователь: {test_user.username}")
        
        # Проверяем текущую роль
        if hasattr(test_user, 'profile'):
            current_role = test_user.profile.role
            print(f"📊 Текущая роль: {current_role}")
            
            if current_role == 'dispatcher':
                print("✅ Пользователь уже является диспетчером!")
                return
            
            # Обновляем роль
            test_user.profile.role = 'dispatcher'
            test_user.profile.bio = 'Тестовый пользователь-диспетчер'
            test_user.profile.save()
            
            print(f"✅ Роль изменена с '{current_role}' на 'dispatcher'")
            
        else:
            # Создаем профиль с ролью диспетчера
            profile = UserProfile.objects.create(
                user=test_user,
                role='dispatcher',
                phone='+7900000000',
                bio='Тестовый пользователь-диспетчер'
            )
            print("✅ Создан профиль диспетчера")
            
        # Проверяем результат
        test_user.refresh_from_db()
        print(f"🎯 Финальная роль: {test_user.profile.role}")
        
    except User.DoesNotExist:
        print("❌ Тестовый пользователь не найден. Он будет создан автоматически при первом запросе.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    update_test_user_role()