#!/usr/bin/env python

import os
import sys
import django
import google.generativeai as genai

# Добавляем путь к проекту
sys.path.append('/Users/imac5/Desktop/98hgfd/truck/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'truck_platform.settings')
django.setup()

from django.conf import settings

def list_available_models():
    print("🔍 Получаем список доступных моделей...")
    
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        print("❌ API ключ не настроен")
        return
    
    try:
        genai.configure(api_key=api_key)
        
        models = genai.list_models()
        
        print(f"📋 Найдено моделей: {len(list(models))}")
        
        # Перезапрашиваем модели для итерации
        models = genai.list_models()
        
        for model in models:
            print(f"📄 Модель: {model.name}")
            print(f"   Поддерживаемые методы: {model.supported_generation_methods}")
            print(f"   Описание: {model.description if hasattr(model, 'description') else 'N/A'}")
            print("   ---")
            
    except Exception as e:
        print(f"❌ Ошибка получения моделей: {e}")

if __name__ == "__main__":
    list_available_models()