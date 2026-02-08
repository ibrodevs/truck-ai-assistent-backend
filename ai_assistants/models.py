from django.db import models
from django.contrib.auth.models import User


class AIAssistantType(models.TextChoices):
    LEGAL = 'legal', 'Юридический ассистент'
    DRIVER_MATCHING = 'driver_matching', 'Подбор водителей'
    GENERAL_HELPER = 'general_helper', 'Помощник'


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    assistant_type = models.CharField(max_length=20, choices=AIAssistantType.choices)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_assistant_type_display()} - {self.title or 'Без названия'}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user_message = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        sender = "Пользователь" if self.is_user_message else "ИИ"
        return f"{sender}: {self.content[:50]}..."


class DriverMatchingRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    route_type = models.CharField(max_length=255)
    driver_requirements = models.TextField()
    dates = models.CharField(max_length=255)
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Запрос на водителя - {self.route_type} - {self.created_at.date()}"
