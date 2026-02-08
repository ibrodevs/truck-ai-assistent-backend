from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, DriverAvailability


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'user', 'role', 'role_display', 'company', 'phone', 'is_blocked', 'created_at',
            'bio', 'experience_years', 'driver_license', 'license_categories', 
            'skills', 'preferred_routes', 'available'
        ]


class DriverProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения профилей водителей при подборе"""
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'username', 'first_name', 'last_name', 'phone', 'company',
            'bio', 'experience_years', 'driver_license', 'license_categories',
            'skills', 'preferred_routes', 'available'
        ]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    role = serializers.ChoiceField(choices=UserProfile.USER_ROLES, default='trucker')
    company = serializers.CharField(max_length=255, required=False)
    phone = serializers.CharField(max_length=20, required=False)
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value
    
    def create(self, validated_data):
        # Извлекаем данные профиля до создания пользователя
        profile_data = {
            'role': validated_data.pop('role', 'trucker'),
            'company': validated_data.pop('company', ''),
            'phone': validated_data.pop('phone', ''),
        }
        
        # Создаем пользователя (signal автоматически создаст профиль)
        user = User.objects.create_user(**validated_data)
        
        # Обновляем профиль с правильными данными
        profile = user.profile
        profile.role = profile_data['role']
        profile.company = profile_data['company']
        profile.phone = profile_data['phone']
        profile.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    if hasattr(user, 'profile') and user.profile.is_blocked:
                        raise serializers.ValidationError("Ваш аккаунт заблокирован")
                    data['user'] = user
                else:
                    raise serializers.ValidationError("Аккаунт не активен")
            else:
                raise serializers.ValidationError("Неверные учетные данные")
        else:
            raise serializers.ValidationError("Необходимо указать имя пользователя и пароль")
        
        return data