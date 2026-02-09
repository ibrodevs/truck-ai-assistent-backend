#!/usr/bin/env python

import requests
import json

def test_driver_matching():
    """Тест API подбора водителей на продакшене"""
    
    base_url = "https://truck-ai-assistent-backend.onrender.com"
    endpoint = f"{base_url}/api/ai/driver-matching/"
    
    # Тестовые данные для подбора водителя
    payload = {
        "route_type": "Междугородний рейс Москва-СПб",
        "driver_requirements": "Нужен водитель с опытом работы на дальних маршрутах, категория CE",
        "dates": "с 15 февраля по 20 февраля 2026"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🚛 Тестируем API подбора водителей...")
        print(f"📍 URL: {endpoint}")
        print(f"📤 Запрос: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Успешный ответ!")
            print(f"🎯 AI ответ: {data.get('ai_response', 'Нет ответа')[:200]}...")
            
            if 'drivers' in data:
                drivers_count = len(data['drivers'])
                print(f"👥 Найдено водителей: {drivers_count}")
                
                if drivers_count > 0:
                    for i, driver in enumerate(data['drivers'][:3], 1):  # Показываем первых 3
                        print(f"  {i}. {driver.get('name', 'Неизвестно')}")
                        print(f"     📞 {driver.get('phone', 'Нет телефона')}")
                        print(f"     🚚 Опыт: {driver.get('experience_years', 0)} лет")
                        
        elif response.status_code == 403:
            error_data = response.json()
            print("❌ Доступ запрещен!")
            print(f"🚨 Сообщение: {error_data.get('error', 'Неизвестная ошибка')}")
            print("💡 Возможно нужно время для деплоя изменений...")
            
        else:
            print(f"❌ Ошибка {response.status_code}")
            try:
                error_data = response.json()
                print(f"🚨 Детали: {error_data}")
            except:
                print(f"🚨 Текст ошибки: {response.text}")
                
    except Exception as e:
        print(f"❌ Исключение: {e}")

def check_user_role():
    """Проверяем роль пользователя через API"""
    
    base_url = "https://truck-ai-assistent-backend.onrender.com"
    
    # Сначала попробуем отправить сообщение чтобы создать пользователя
    chat_endpoint = f"{base_url}/api/ai/send-message/"
    chat_payload = {
        "message": "Проверка роли пользователя",
        "assistant_type": "general_helper"
    }
    
    try:
        print("👤 Проверяем роль пользователя...")
        requests.post(chat_endpoint, json=chat_payload, headers={"Content-Type": "application/json"}, timeout=10)
        print("✅ Пользователь инициализирован")
    except:
        print("⚠️ Не удалось инициализировать пользователя")

if __name__ == "__main__":
    check_user_role()
    print()
    test_driver_matching()