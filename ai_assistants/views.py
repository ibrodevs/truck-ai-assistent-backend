from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404

from .models import Conversation, Message, DriverMatchingRequest, AIAssistantType
from .serializers import (
    ConversationSerializer, ConversationListSerializer, SendMessageSerializer,
    DriverMatchingSerializer, DriverMatchingRequestSerializer
)
from .services import GeminiService


class ConversationListView(ListAPIView):
    serializer_class = ConversationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)


class ConversationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            user=request.user
        )
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request):
    serializer = SendMessageSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_message = serializer.validated_data['message']
    assistant_type = serializer.validated_data['assistant_type']
    conversation_id = serializer.validated_data.get('conversation_id')
    
    # Получаем или создаем диалог
    if conversation_id:
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            user=request.user
        )
    else:
        conversation = Conversation.objects.create(
            user=request.user,
            assistant_type=assistant_type,
            title=user_message[:50] + ('...' if len(user_message) > 50 else '')
        )
    
    # Сохраняем сообщение пользователя
    user_msg = Message.objects.create(
        conversation=conversation,
        content=user_message,
        is_user_message=True
    )
    
    # Генерируем ответ ИИ
    gemini_service = GeminiService()
    conversation_history = conversation.messages.all()
    
    ai_response = gemini_service.generate_response(
        user_message=user_message,
        assistant_type=assistant_type,
        conversation_history=conversation_history
    )
    
    # Сохраняем ответ ИИ
    ai_msg = Message.objects.create(
        conversation=conversation,
        content=ai_response,
        is_user_message=False
    )
    
    return Response({
        'conversation_id': conversation.id,
        'user_message': {
            'id': user_msg.id,
            'content': user_msg.content,
            'is_user_message': True,
            'created_at': user_msg.created_at
        },
        'ai_response': {
            'id': ai_msg.id,
            'content': ai_msg.content,
            'is_user_message': False,
            'created_at': ai_msg.created_at
        }
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def driver_matching(request):
    serializer = DriverMatchingRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    route_type = serializer.validated_data['route_type']
    driver_requirements = serializer.validated_data['driver_requirements']
    dates = serializer.validated_data['dates']
    
    # Генерируем ответ ИИ
    gemini_service = GeminiService()
    ai_response = gemini_service.generate_driver_matching_response(
        route_type=route_type,
        driver_requirements=driver_requirements,
        dates=dates
    )
    
    # Сохраняем запрос
    matching_request = DriverMatchingRequest.objects.create(
        user=request.user,
        route_type=route_type,
        driver_requirements=driver_requirements,
        dates=dates,
        ai_response=ai_response
    )
    
    serializer = DriverMatchingSerializer(matching_request)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def driver_matching_history(request):
    requests = DriverMatchingRequest.objects.filter(user=request.user).order_by('-created_at')
    serializer = DriverMatchingSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def assistant_types(request):
    """Получить список доступных типов ассистентов"""
    return Response([
        {'value': choice[0], 'label': choice[1]} 
        for choice in AIAssistantType.choices
    ])
