#!/usr/bin/env python

import os
import sys
import django

# Добавляем путь к проекту
sys.path.append('/Users/imac5/Desktop/98hgfd/truck/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'truck_platform.settings')
django.setup()

import google.genai as genai
from django.conf import settings

def test_new_genai_api():
    """Тестируем новый Google Genai API"""
    
    try:
        api_key = settings.GEMINI_API_KEY
        print(f"🔑 API ключ: {'Установлен' if api_key and len(api_key) > 10 else 'Не установлен'}")
        
        if not api_key:
            print("❌ API ключ не настроен")
            return
        
        # Создаем клиент
        client = genai.Client(api_key=api_key)
        print("✅ Клиент создан успешно")
        
        # Тестовый запрос
        prompt = "Привет! Сколько будет 2+2?"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[{'parts': [{'text': prompt}]}]
        )
        
        print(f"📤 Запрос: {prompt}")
        
        if hasattr(response, 'text'):
            print(f"📥 Ответ (text): {response.text}")
        elif hasattr(response, 'candidates') and response.candidates:
            answer = response.candidates[0].content.parts[0].text
            print(f"📥 Ответ (candidates): {answer}")
        else:
            print(f"❓ Неизвестный формат ответа: {type(response)}")
            print(f"Attributes: {dir(response)}")
        
        print("✅ Новый API работает!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_genai_api()