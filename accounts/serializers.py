from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, DriverAvailability, DriverRating


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
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'first_name', 'last_name', 'phone', 'company',
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


class DriverAvailabilitySerializer(serializers.ModelSerializer):
    """Сериализатор для календаря доступности водителя"""
    driver_username = serializers.CharField(source='driver.user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DriverAvailability
        fields = [
            'id', 'driver', 'driver_username', 'start_date', 'end_date', 
            'status', 'status_display', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'driver', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Проверяем, что дата окончания не раньше даты начала"""
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("Дата окончания не может быть раньше даты начала")
        return data


class DriverRatingSerializer(serializers.ModelSerializer):
    """Сериализатор для рейтингов водителей"""
    driver_username = serializers.CharField(source='driver.user.username', read_only=True)
    driver_full_name = serializers.SerializerMethodField()
    rated_by_username = serializers.CharField(source='rated_by.user.username', read_only=True)
    
    class Meta:
        model = DriverRating
        fields = [
            'id', 'driver', 'driver_username', 'driver_full_name',
            'rated_by', 'rated_by_username', 'rating', 'comment',
            'punctuality', 'professionalism', 'communication',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'rated_by', 'created_at', 'updated_at']
    
    def get_driver_full_name(self, obj):
        return f"{obj.driver.user.first_name} {obj.driver.user.last_name}".strip()
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5")
        return value
    
    def validate(self, data):
        """Проверяем, что водитель не может оценить сам себя"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            driver = data.get('driver')
            if driver and driver.user == request.user:
                raise serializers.ValidationError("Вы не можете оценить сам себя")
        return data


class DriverAverageRatingSerializer(serializers.Serializer):
    """Сериализатор для средних рейтингов водителя"""
    average_rating = serializers.FloatField()
    total_ratings = serializers.IntegerField()
    punctuality = serializers.FloatField()
    professionalism = serializers.FloatField()
    communication = serializers.FloatField()
