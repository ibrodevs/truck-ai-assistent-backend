from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notifications_list_view(request):
    """Получить список уведомлений текущего пользователя"""
    profile = request.user.profile
    notifications = Notification.objects.filter(recipient=profile)
    
    # Фильтр по прочитанным/непрочитанным
    is_read = request.query_params.get('is_read')
    if is_read is not None:
        is_read_bool = is_read.lower() in ('true', '1', 'yes')
        notifications = notifications.filter(is_read=is_read_bool)
    
    # Лимит количества
    limit = request.query_params.get('limit')
    if limit:
        try:
            notifications = notifications[:int(limit)]
        except ValueError:
            pass
    
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notifications_unread_count_view(request):
    """Получить количество непрочитанных уведомлений"""
    profile = request.user.profile
    count = Notification.objects.filter(recipient=profile, is_read=False).count()
    return Response({'unread_count': count})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def notification_mark_read_view(request, pk):
    """Пометить уведомление как прочитанное"""
    profile = request.user.profile
    
    try:
        notification = Notification.objects.get(pk=pk, recipient=profile)
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Уведомление не найдено'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
    
    serializer = NotificationSerializer(notification)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def notification_mark_all_read_view(request):
    """Пометить все уведомления как прочитанные"""
    profile = request.user.profile
    
    updated_count = Notification.objects.filter(
        recipient=profile,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return Response({
        'message': f'Отмечено {updated_count} уведомлений как прочитанные',
        'updated_count': updated_count
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def notification_delete_view(request, pk):
    """Удалить уведомление"""
    profile = request.user.profile
    
    try:
        notification = Notification.objects.get(pk=pk, recipient=profile)
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Уведомление не найдено'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    notification.delete()
    return Response(
        {'message': 'Уведомление удалено'},
        status=status.HTTP_204_NO_CONTENT
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def notification_create_view(request):
    """Создать уведомление (для тестирования или системных уведомлений)"""
    profile = request.user.profile
    
    # Только админы могут создавать уведомления для других пользователей
    if profile.role != 'admin' and 'recipient' in request.data:
        return Response(
            {'error': 'Недостаточно прав'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        # Если получатель не указан, создаем для текущего пользователя
        recipient = profile
        if 'recipient_id' in request.data and profile.role == 'admin':
            from accounts.models import UserProfile
            try:
                recipient = UserProfile.objects.get(id=request.data['recipient_id'])
            except UserProfile.DoesNotExist:
                pass
        
        serializer.save(recipient=recipient)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
