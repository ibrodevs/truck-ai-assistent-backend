#!/usr/bin/env python

import os
import sys
import django

# Добавляем путь к проекту
sys.path.append('/Users/imac5/Desktop/98hgfd/truck/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'truck_platform.settings')
django.setup()

from ai_assistants.services import GeminiService
from ai_assistants.models import AIAssistantType

def test_gemini_api():
    print("🧪 Тестируем Gemini API...")
    
    service = GeminiService()
    
    if not service.model:
        print("❌ Gemini API не инициализирован. Проверьте API ключ.")
        return
    
    print("✅ Gemini API инициализирован успешно")
    
    # Тест простого сообщения
    test_message = "Привет! Как дела?"
    
    try:
        response = service.generate_response(
            user_message=test_message,
            assistant_type=AIAssistantType.GENERAL_HELPER
        )
        
        print(f"\n📤 Отправленное сообщение: {test_message}")
        print(f"📥 Ответ ИИ: {response[:200]}...")
        
        if "демо-версия" in response.lower() or "api ключ" in response.lower():
            print("⚠️  Получен демо-ответ. Возможно, проблемы с API ключом.")
        else:
            print("✅ Получен ответ от ИИ!")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

if __name__ == "__main__":
    test_gemini_api()