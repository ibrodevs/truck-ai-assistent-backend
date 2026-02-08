from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import UserProfile, DriverRating
from ai_assistants.models import Conversation, Message
from notifications.models import Notification


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analytics_overview_view(request):
    """Получить общую аналитику для пользователя"""
    profile = request.user.profile
    user = request.user
    
    # Подсчет разговоров
    conversations_count = Conversation.objects.filter(user=user).count()
    
    # Подсчет сообщений
    messages_count = Message.objects.filter(conversation__user=user).count()
    
    # Непрочитанные уведомления
    unread_notifications = Notification.objects.filter(
        recipient=profile,
        is_read=False
    ).count()
    
    # Активность за последние 7 дней
    week_ago = timezone.now() - timedelta(days=7)
    recent_conversations = Conversation.objects.filter(
        user=user,
        created_at__gte=week_ago
    ).count()
    
    recent_messages = Message.objects.filter(
        conversation__user=user,
        created_at__gte=week_ago
    ).count()
    
    # Для водителей - их рейтинг
    driver_stats = None
    if profile.role == 'trucker':
        driver_stats = DriverRating.get_driver_average_rating(profile)
    
    # Статистика по типам ассистентов
    assistant_stats = []
    for assistant_type, display_name in [
        ('legal', 'Юридический'),
        ('driver_matching', 'Подбор водителей'),
        ('general_helper', 'Общий помощник')
    ]:
        count = Conversation.objects.filter(
            user=user,
            assistant_type=assistant_type
        ).count()
        assistant_stats.append({
            'type': assistant_type,
            'name': display_name,
            'sessions': count
        })
    
    return Response({
        'total_conversations': conversations_count,
        'total_messages': messages_count,
        'unread_notifications': unread_notifications,
        'recent_conversations': recent_conversations,
        'recent_messages': recent_messages,
        'driver_rating': driver_stats,
        'assistant_stats': assistant_stats
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analytics_activity_view(request):
    """Получить детальную активность по дням"""
    user = request.user
    days = int(request.query_params.get('days', 7))
    
    activity_data = []
    for i in range(days):
        date = timezone.now().date() - timedelta(days=i)
        start_of_day = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.min.time()))
        end_of_day = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.max.time()))
        
        conversations = Conversation.objects.filter(
            user=user,
            created_at__gte=start_of_day,
            created_at__lte=end_of_day
        ).count()
        
        messages = Message.objects.filter(
            conversation__user=user,
            created_at__gte=start_of_day,
            created_at__lte=end_of_day
        ).count()
        
        activity_data.append({
            'date': date.strftime('%d.%m.%Y'),
            'conversations': conversations,
            'messages': messages
        })
    
    return Response(list(reversed(activity_data)))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analytics_admin_view(request):
    """Административная аналитика (только для админов)"""
    profile = request.user.profile
    
    if profile.role != 'admin':
        return Response(
            {'error': 'Недостаточно прав'},
            status=403
        )
    
    # Общее количество пользователей
    total_users = UserProfile.objects.count()
    truckers_count = UserProfile.objects.filter(role='trucker').count()
    dispatchers_count = UserProfile.objects.filter(role='dispatcher').count()
    
    # Активные пользователи (за последние 7 дней)
    week_ago = timezone.now() - timedelta(days=7)
    active_users = Conversation.objects.filter(
        created_at__gte=week_ago
    ).values('user').distinct().count()
    
    # Всего разговоров и сообщений
    total_conversations = Conversation.objects.count()
    total_messages = Message.objects.count()
    
    # Средний рейтинг водителей
    avg_driver_rating = DriverRating.objects.aggregate(
        Avg('rating')
    )['rating__avg'] or 0
    
    # Популярность ассистентов
    assistant_usage = []
    for assistant_type, display_name in [
        ('legal', 'Юридический'),
        ('driver_matching', 'Подбор водителей'),
        ('general_helper', 'Общий помощник')
    ]:
        count = Conversation.objects.filter(assistant_type=assistant_type).count()
        assistant_usage.append({
            'type': assistant_type,
            'name': display_name,
            'usage': count
        })
    
    return Response({
        'total_users': total_users,
        'truckers_count': truckers_count,
        'dispatchers_count': dispatchers_count,
        'active_users': active_users,
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'average_driver_rating': round(avg_driver_rating, 2),
        'assistant_usage': assistant_usage
    })
