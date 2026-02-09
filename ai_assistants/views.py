from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import Conversation, Message, DriverMatchingRequest, AIAssistantType
from .serializers import (
    ConversationSerializer, ConversationListSerializer, SendMessageSerializer,
    DriverMatchingSerializer, DriverMatchingRequestSerializer
)
from .services import GeminiService


def get_user_for_request(request):
    """Получить пользователя для запроса (временная функция для тестирования)"""
    if not request.user.is_authenticated:
        test_user, _ = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        # Создаем профиль если его нет
        from accounts.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'role': 'trucker',
                'phone': '+7900000000',
                'bio': 'Тестовый пользователь'
            }
        )
        return test_user
    return request.user


class ConversationListView(ListAPIView):
    serializer_class = ConversationListSerializer
    permission_classes = [permissions.AllowAny]  # Временно для тестирования
    
    def get_queryset(self):
        # Временно: если пользователь не авторизован, используем тестового
        if not self.request.user.is_authenticated:
            test_user, _ = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'test@example.com'}
            )
            return Conversation.objects.filter(user=test_user)
        return Conversation.objects.filter(user=self.request.user)


class ConversationDetailView(APIView):
    permission_classes = [permissions.AllowAny]  # Временно для тестирования
    
    def get(self, request, conversation_id):
        # Временно: если пользователь не авторизован, используем тестового
        if not request.user.is_authenticated:
            test_user, _ = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'test@example.com'}
            )
            user = test_user
        else:
            user = request.user
            
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            user=user
        )
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Временно для тестирования
def send_message(request):
    serializer = SendMessageSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = get_user_for_request(request)
    user_message = serializer.validated_data['message']
    assistant_type = serializer.validated_data['assistant_type']
    conversation_id = serializer.validated_data.get('conversation_id')
    
    # Проверка доступа к ассистенту по роли пользователя
    user_role = user.profile.role if hasattr(user, 'profile') else 'trucker'
    if assistant_type == 'driver_matching' and user_role == 'trucker':
        return Response(
            {'error': 'У вас нет доступа к этому ассистенту. Подбор водителей доступен только диспетчерам.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Получаем или создаем диалог
    if conversation_id:
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            user=user
        )
    else:
        conversation = Conversation.objects.create(
            user=user,
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
@permission_classes([permissions.AllowAny])  # Временно для тестирования
def driver_matching(request):
    user = get_user_for_request(request)
    # Проверка прав доступа - только диспетчеры и администраторы
    user_role = user.profile.role if hasattr(user, 'profile') else 'trucker'
    if user_role == 'trucker':
        return Response(
            {'error': 'Доступ запрещен. Функция подбора водителей доступна только диспетчерам.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = DriverMatchingRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    route_type = serializer.validated_data['route_type']
    driver_requirements = serializer.validated_data['driver_requirements']
    dates = serializer.validated_data['dates']
    
    # Получаем всех доступных водителей из базы данных
    from accounts.models import UserProfile, DriverAvailability
    from accounts.serializers import DriverProfileSerializer, DriverAvailabilitySerializer
    from datetime import datetime, date
    
    # Парсим даты из запроса (если указаны)
    start_date = None
    end_date = None
    if dates:
        try:
            # Попробуем извлечь даты из строки
            import re
            date_pattern = r'\d{4}-\d{2}-\d{2}'
            found_dates = re.findall(date_pattern, dates)
            if len(found_dates) >= 2:
                start_date = datetime.strptime(found_dates[0], '%Y-%m-%d').date()
                end_date = datetime.strptime(found_dates[1], '%Y-%m-%d').date()
            elif len(found_dates) == 1:
                start_date = datetime.strptime(found_dates[0], '%Y-%m-%d').date()
        except:
            pass
    
    # Получаем всех водителей с базовой доступностью
    available_drivers = UserProfile.objects.filter(
        role='trucker',
        available=True
    ).select_related('user')
    
    # Сериализуем данные водителей
    drivers_data = []
    for driver in available_drivers:
        driver_info = DriverProfileSerializer(driver).data
        
        # Получаем записи календаря водителя
        availability_entries = DriverAvailability.objects.filter(driver=driver)
        
        # Проверяем доступность на указанные даты
        if start_date and end_date:
            # Находим все записи, пересекающиеся с запрашиваемым периодом
            relevant_entries = availability_entries.filter(
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            # Собираем информацию о доступности
            calendar_info = []
            is_available_for_period = True
            
            for entry in relevant_entries:
                calendar_info.append({
                    'start_date': entry.start_date.isoformat(),
                    'end_date': entry.end_date.isoformat(),
                    'status': entry.status,
                    'notes': entry.notes
                })
                
                # Если есть хотя бы одна запись "занят" в этом периоде
                if entry.status == 'busy':
                    is_available_for_period = False
            
            driver_info['calendar_status'] = 'available' if is_available_for_period else 'busy'
            driver_info['calendar_entries'] = calendar_info
        else:
            # Если даты не указаны, показываем ближайшие записи
            upcoming_entries = availability_entries.filter(
                start_date__gte=date.today()
            ).order_by('start_date')[:5]
            
            driver_info['calendar_entries'] = [
                {
                    'start_date': entry.start_date.isoformat(),
                    'end_date': entry.end_date.isoformat(),
                    'status': entry.status,
                    'notes': entry.notes
                }
                for entry in upcoming_entries
            ]
            driver_info['calendar_status'] = 'unknown'
        
        drivers_data.append(driver_info)
    
    print(f"Найдено водителей для подбора: {len(drivers_data)}")
    
    # Генерируем ответ ИИ с учетом реальных водителей и их календарей
    gemini_service = GeminiService()
    ai_response = gemini_service.generate_driver_matching_response(
        route_type=route_type,
        driver_requirements=driver_requirements,
        dates=dates,
        drivers_data=drivers_data  # Передаем данные водителей с календарями
    )
    
    # Сохраняем запрос
    matching_request = DriverMatchingRequest.objects.create(
        user=user,
        route_type=route_type,
        driver_requirements=driver_requirements,
        dates=dates,
        ai_response=ai_response
    )
    
    serializer = DriverMatchingSerializer(matching_request)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Временно для тестирования
def driver_matching_history(request):
    user = get_user_for_request(request)
    # Проверка прав доступа - только диспетчеры и администраторы
    user_role = user.profile.role if hasattr(user, 'profile') else 'trucker'
    if user_role == 'trucker':
        return Response(
            {'error': 'Доступ запрещен. Функция подбора водителей доступна только диспетчерам.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    requests = DriverMatchingRequest.objects.filter(user=user).order_by('-created_at')
    serializer = DriverMatchingSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def assistant_types(request):
    """Получить список доступных типов ассистентов"""
    return Response([
        {'value': choice[0], 'label': choice[1]} 
        for choice in AIAssistantType.choices
    ])
