from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import UserProfile
from .serializers import UserProfileSerializer, RegisterSerializer, LoginSerializer


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def csrf_token_view(request):
    """Получить CSRF токен"""
    return Response({'csrfToken': get_token(request)})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    print("Register request data:", request.data)
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        
        profile_serializer = UserProfileSerializer(user.profile)
        return Response({
            'message': 'Регистрация успешна',
            'user': profile_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
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
