from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime

from .models import UserProfile, DriverAvailability, DriverRating
from .serializers import UserProfileSerializer, RegisterSerializer, LoginSerializer, DriverAvailabilitySerializer, DriverRatingSerializer, DriverAverageRatingSerializer, DriverProfileSerializer


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def csrf_token_view(request):
    """Получить CSRF токен"""
    return Response({'csrfToken': get_token(request)})


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    print("Register request data:", request.data)
    print("Role from request:", request.data.get('role'))
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        print(f"User created: {user.username}, Profile role: {user.profile.role}")
        login(request, user)
        
        profile_serializer = UserProfileSerializer(user.profile)
        print("Profile data returned:", profile_serializer.data)
        return Response({
            'message': 'Регистрация успешна',
            'user': profile_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    print("Login request received:", request.method)
    print("Login request data:", request.data)
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        profile_serializer = UserProfileSerializer(user.profile)
        return Response({
            'message': 'Вход выполнен успешно',
            'user': profile_serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Выход выполнен успешно'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    profile_serializer = UserProfileSerializer(request.user.profile)
    return Response(profile_serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile_view(request):
    """Обновление профиля пользователя (особенно для водителей)"""
    profile = request.user.profile
    
    # Обновляем только разрешенные поля
    allowed_fields = [
        'company', 'phone', 'bio', 'experience_years',
        'driver_license', 'license_categories', 'skills',
        'preferred_routes', 'available'
    ]
    
    for field in allowed_fields:
        if field in request.data:
            setattr(profile, field, request.data[field])
    
    profile.save()
    
    serializer = UserProfileSerializer(profile)
    return Response({
        'message': 'Профиль успешно обновлен',
        'profile': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_auth(request):
    """Проверка авторизации пользователя"""
    if request.user.is_authenticated:
        profile_serializer = UserProfileSerializer(request.user.profile)
        return Response({
            'authenticated': True,
            'user': profile_serializer.data
        })
    else:
        return Response({'authenticated': False})


# === КАЛЕНДАРЬ ДОСТУПНОСТИ ===

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def availability_list_view(request):
    """Получить список записей календаря для текущего водителя"""
    profile = request.user.profile
    
    # Только водители могут просматривать свой календарь
    if profile.role != 'trucker':
        return Response(
            {'error': 'Только водители могут использовать календарь'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    entries = DriverAvailability.objects.filter(driver=profile)
    serializer = DriverAvailabilitySerializer(entries, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def availability_create_view(request):
    """Создать новую запись в календаре"""
    profile = request.user.profile
    
    # Только водители могут создавать записи
    if profile.role != 'trucker':
        return Response(
            {'error': 'Только водители могут использовать календарь'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = DriverAvailabilitySerializer(data=request.data)
    if serializer.is_valid():
        # Автоматически привязываем к профилю текущего пользователя
        serializer.save(driver=profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def availability_update_view(request, pk):
    """Обновить запись в календаре"""
    profile = request.user.profile
    
    try:
        entry = DriverAvailability.objects.get(pk=pk, driver=profile)
    except DriverAvailability.DoesNotExist:
        return Response(
            {'error': 'Запись не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = DriverAvailabilitySerializer(entry, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def availability_delete_view(request, pk):
    """Удалить запись из календаря"""
    profile = request.user.profile
    
    try:
        entry = DriverAvailability.objects.get(pk=pk, driver=profile)
    except DriverAvailability.DoesNotExist:
        return Response(
            {'error': 'Запись не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    entry.delete()
    return Response(
        {'message': 'Запись успешно удалена'},
        status=status.HTTP_204_NO_CONTENT
    )


# === РЕЙТИНГИ ВОДИТЕЛЕЙ ===

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def driver_ratings_list_view(request, driver_id=None):
    """Получить список рейтингов водителя"""
    if driver_id:
        try:
            driver = UserProfile.objects.get(id=driver_id, role='trucker')
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Водитель не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        ratings = DriverRating.objects.filter(driver=driver)
    else:
        # Если ID не указан, показываем все рейтинги (для админов)
        if request.user.profile.role != 'admin':
            return Response(
                {'error': 'Недостаточно прав'},
                status=status.HTTP_403_FORBIDDEN
            )
        ratings = DriverRating.objects.all()
    
    serializer = DriverRatingSerializer(ratings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def driver_average_rating_view(request, driver_id):
    """Получить средний рейтинг водителя"""
    try:
        driver = UserProfile.objects.get(id=driver_id, role='trucker')
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Водитель не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    avg_rating = DriverRating.get_driver_average_rating(driver)
    if avg_rating is None:
        return Response({
            'average_rating': 0,
            'total_ratings': 0,
            'punctuality': 0,
            'professionalism': 0,
            'communication': 0,
        })
    
    serializer = DriverAverageRatingSerializer(avg_rating)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def driver_rating_create_view(request):
    """Создать рейтинг для водителя"""
    serializer = DriverRatingSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # Проверяем, что пользователь не оценивал этого водителя ранее
        driver_id = request.data.get('driver')
        existing_rating = DriverRating.objects.filter(
            driver_id=driver_id,
            rated_by=request.user.profile
        ).first()
        
        if existing_rating:
            return Response(
                {'error': 'Вы уже оценили этого водителя. Вы можете обновить существующий рейтинг.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(rated_by=request.user.profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def driver_rating_update_view(request, pk):
    """Обновить существующий рейтинг"""
    try:
        rating = DriverRating.objects.get(pk=pk, rated_by=request.user.profile)
    except DriverRating.DoesNotExist:
        return Response(
            {'error': 'Рейтинг не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = DriverRatingSerializer(
        rating, 
        data=request.data, 
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def driver_rating_delete_view(request, pk):
    """Удалить рейтинг"""
    profile = request.user.profile
    
    try:
        # Пользователи могут удалять только свои рейтинги, админы - любые
        if profile.role == 'admin':
            rating = DriverRating.objects.get(pk=pk)
        else:
            rating = DriverRating.objects.get(pk=pk, rated_by=profile)
    except DriverRating.DoesNotExist:
        return Response(
            {'error': 'Рейтинг не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    rating.delete()
    return Response(
        {'message': 'Рейтинг удален'},
        status=status.HTTP_204_NO_CONTENT
    )


# === СПИСОК ВОДИТЕЛЕЙ ===

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def drivers_list_view(request):
    """Получить список всех водителей (для диспетчеров и админов)"""
    profile = request.user.profile
    
    # Только диспетчеры и админы могут просматривать список водителей
    if profile.role not in ['dispatcher', 'admin']:
        return Response(
            {'error': 'Недостаточно прав'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    drivers = UserProfile.objects.filter(role='trucker')
    serializer = DriverProfileSerializer(drivers, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def driver_detail_view(request, driver_id):
    """Получить детальную информацию о водителе"""
    try:
        driver = UserProfile.objects.get(id=driver_id, role='trucker')
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Водитель не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = DriverProfileSerializer(driver)
    return Response(serializer.data)
