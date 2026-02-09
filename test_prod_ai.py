#!/usr/bin/env python

import os
import sys
import django

# Добавляем путь к проекту
sys.path.append('/Users/imac5/Desktop/98hgfd/truck/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'truck_platform.settings')
django.setup()

import requests
import json

def test_ai_endpoint():
    """Тест AI endpoint через API"""
    
    base_url = "https://truck-ai-assistent-backend.onrender.com"
    
    # Тестируем AI чат endpoint
    ai_url = f"{base_url}/api/ai/send-message/"
    
    payload = {
        "message": "Привет! Как ты можешь помочь водителю грузовика?",
        "assistant_type": "ROUTE_OPTIMIZER"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🌐 Тестируем AI API на продакшене...")
        print(f"📍 URL: {ai_url}")
        print(f"📤 Отправляем: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(ai_url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Успешный ответ:")
            print(f"📥 Ответ: {data.get('response', 'Нет ответа')}")
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
    test_ai_endpoint()