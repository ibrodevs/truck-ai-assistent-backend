from django.contrib import admin
from .models import Conversation, Message, DriverMatchingRequest


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['user', 'assistant_type', 'title', 'created_at', 'updated_at']
    list_filter = ['assistant_type', 'created_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'is_user_message', 'content_preview', 'created_at']
    list_filter = ['is_user_message', 'created_at']
    search_fields = ['content']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Содержание'


@admin.register(DriverMatchingRequest)
class DriverMatchingRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'route_type', 'dates', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'route_type']
    readonly_fields = ['created_at']
