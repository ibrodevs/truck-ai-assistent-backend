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

def quick_test():
    """Быстрый тест AI API"""
    
    base_url = "https://truck-ai-assistent-backend.onrender.com"
    ai_url = f"{base_url}/api/ai/send-message/"
    
    payload = {
        "message": "Помоги оптимизировать маршрут доставки!",
        "assistant_type": "general_helper"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        print("🤖 Тестируем AI чат...")
        response = requests.post(ai_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            ai_content = data.get('ai_response', {}).get('content', '')
            
            print("✅ AI отвечает!")
            print(f"📩 Пользователь: {payload['message']}")
            print(f"🤖 AI: {ai_content[:200]}...")
            
            # Проверяем реальность ответа
            if "демо-версия" in ai_content:
                print("⚠️  Fallback ответ (демо)")
            else:
                print("🎯 Реальный AI ответ!")
                
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")

if __name__ == "__main__":
    quick_test()