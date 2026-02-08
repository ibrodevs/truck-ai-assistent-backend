from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


class UserProfile(models.Model):
    USER_ROLES = [
        ('trucker', 'Водитель'),
        ('dispatcher', 'Диспетчер'),
        ('admin', 'Администратор'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='trucker')
    company = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Поля для водителей
    bio = models.TextField(blank=True, verbose_name='О себе')
    experience_years = models.IntegerField(default=0, verbose_name='Опыт работы (лет)')
    driver_license = models.CharField(max_length=100, blank=True, verbose_name='Водительское удостоверение')
    license_categories = models.CharField(max_length=50, blank=True, verbose_name='Категории (например: B, C, CE)')
    skills = models.TextField(blank=True, verbose_name='Навыки и умения')
    preferred_routes = models.CharField(max_length=255, blank=True, verbose_name='Предпочитаемые маршруты')
    available = models.BooleanField(default=True, verbose_name='Доступен для работы')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class DriverAvailability(models.Model):
    """Календарь доступности водителя"""
    STATUS_CHOICES = [
        ('available', 'Свободен'),
        ('busy', 'Занят'),
    ]
    
    driver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='availability_entries')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='Статус')
    notes = models.TextField(blank=True, verbose_name='Примечания')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
        verbose_name = 'Доступность водителя'
        verbose_name_plural = 'Доступность водителей'
    
    def __str__(self):
        return f"{self.driver.user.username} - {self.start_date} to {self.end_date} ({self.get_status_display()})"
    
    def is_available_on_date(self, check_date):
        """Проверяет, свободен ли водитель в указанную дату"""
        if isinstance(check_date, str):
            check_date = date.fromisoformat(check_date)
        return self.start_date <= check_date <= self.end_date and self.status == 'available'


class DriverRating(models.Model):
    """Система рейтингов водителей"""
    driver = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='ratings',
        limit_choices_to={'role': 'trucker'}
    )
    rated_by = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='given_ratings'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка (1-5)'
    )
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    
    # Критерии оценки
    punctuality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        verbose_name='Пунктуальность'
    )
    professionalism = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        verbose_name='Профессионализм'
    )
    communication = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        verbose_name='Коммуникация'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Рейтинг водителя'
        verbose_name_plural = 'Рейтинги водителей'
        unique_together = ['driver', 'rated_by']
    
    def __str__(self):
        return f"{self.driver.user.username} - {self.rating}/5 от {self.rated_by.user.username}"
    
    @staticmethod
    def get_driver_average_rating(driver_profile):
        """Получить средний рейтинг водителя"""
        ratings = DriverRating.objects.filter(driver=driver_profile)
        if not ratings.exists():
            return None
        
        avg_rating = ratings.aggregate(models.Avg('rating'))['rating__avg']
        avg_punctuality = ratings.aggregate(models.Avg('punctuality'))['punctuality__avg']
        avg_professionalism = ratings.aggregate(models.Avg('professionalism'))['professionalism__avg']
        avg_communication = ratings.aggregate(models.Avg('communication'))['communication__avg']
        
        return {
            'average_rating': round(avg_rating, 2) if avg_rating else 0,
            'total_ratings': ratings.count(),
            'punctuality': round(avg_punctuality, 2) if avg_punctuality else 0,
            'professionalism': round(avg_professionalism, 2) if avg_professionalism else 0,
            'communication': round(avg_communication, 2) if avg_communication else 0,
        }
