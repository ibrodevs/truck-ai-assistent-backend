from rest_framework import serializers
from .models import Conversation, Message, DriverMatchingRequest, AIAssistantType


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'is_user_message', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    assistant_type_display = serializers.CharField(source='get_assistant_type_display', read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'assistant_type', 'assistant_type_display', 'title', 'created_at', 'updated_at', 'messages']


class ConversationListSerializer(serializers.ModelSerializer):
    assistant_type_display = serializers.CharField(source='get_assistant_type_display', read_only=True)
    messages_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'assistant_type', 'assistant_type_display', 'title', 'created_at', 'updated_at', 'messages_count']
    
    def get_messages_count(self, obj):
        return obj.messages.count()


class SendMessageSerializer(serializers.Serializer):
    message = serializers.CharField()
    assistant_type = serializers.ChoiceField(choices=AIAssistantType.choices)
    conversation_id = serializers.IntegerField(required=False)


class DriverMatchingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverMatchingRequest
        fields = ['id', 'route_type', 'driver_requirements', 'dates', 'ai_response', 'created_at']


class DriverMatchingRequestSerializer(serializers.Serializer):
    route_type = serializers.CharField(max_length=255)
    driver_requirements = serializers.CharField()
    dates = serializers.CharField(max_length=255)