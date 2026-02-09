#!/usr/bin/env python

import os
import sys
import django

# Доб            print(f"📥 AI ответ: {data.get('ai_response', {}).get('content', 'Нет ответа')}")вляем путь к проекту
sys.path.append('/Users/imac5/Desktop/98hgfd/truck/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'truck_platform.settings')
django.setup()

import requests
import json

def test_assistant_types():
    """Получить список доступных типов ассистентов"""
    
    base_url = "https://truck-ai-assistent-backend.onrender.com"
    types_url = f"{base_url}/api/ai/assistant-types/"
    
    try:
        print("🔍 Получаем типы ассистентов...")
        response = requests.get(types_url)
        
        print(f"📊 Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Доступные типы ассистентов:")
            for assistant in data:
                print(f"  - {assistant.get('code')}: {assistant.get('name')}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"🚨 Ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")

def test_ai_with_valid_type():
    """Тестируем AI с валидным типом ассистента"""
    
    base_url = "https://truck-ai-assistent-backend.onrender.com"
    ai_url = f"{base_url}/api/ai/send-message/"
    
    # Пробуем с валидным типом из модели
    payload = {
        "message": "Привет! Как дела?",
        "assistant_type": "general_helper"  # используем валидный тип
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("\n🤖 Тестируем AI с lowercase типом...")
        response = requests.post(ai_url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Успешный ответ:")
            print(f"� Полный ответ: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print(f"�📥 AI ответ: {data.get('response', 'Нет ответа')}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            try:
                error_data = response.json()
                print(f"🚨 Детали ошибки: {error_data}")
            except:
                print(f"🚨 Текст ошибки: {response.text}")
                
    except Exception as e:
        print(f"❌ Исключение при запросе: {e}")

if __name__ == "__main__":
    test_assistant_types()
    test_ai_with_valid_type()