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

def test_with_debug():
    """Тест с дебагом для проверки реального AI"""
    
    base_url = "https://truck-ai-assistent-backend.onrender.com"
    ai_url = f"{base_url}/api/ai/send-message/"
    
    # Попробуем со специфическим вопросом
    payload = {
        "message": "Сколько будет 2+2?",
        "assistant_type": "general_helper"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        print("🔍 Тестируем с математическим вопросом...")
        response = requests.post(ai_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            ai_content = data.get('ai_response', {}).get('content', '')
            
            print(f"📩 Вопрос: {payload['message']}")
            print(f"🤖 Ответ: {ai_content}")
            
            # Анализируем ответ
            if "2+2" in ai_content or "4" in ai_content or "четыре" in ai_content:
                print("🎯 AI обрабатывает вопрос!")
            elif "демо-версия" in ai_content:
                print("⚠️  Fallback режим активен")
            else:
                print("❓ Неопределенный тип ответа")
                
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    # Тестируем разные типы ассистентов
    print("\n🔄 Тестируем типы ассистентов:")
    for assistant_type in ["general_helper", "legal", "driver_matching"]:
        print(f"\n📌 Тип: {assistant_type}")
        payload["assistant_type"] = assistant_type
        
        try:
            response = requests.post(ai_url, json=payload, headers=headers, timeout=20)
            if response.status_code == 200:
                data = response.json()
                ai_content = data.get('ai_response', {}).get('content', '')
                print(f"   ✅ Ответ: {ai_content[:100]}...")
            else:
                print(f"   ❌ Ошибка: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_with_debug()