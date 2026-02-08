from django.db import models
from django.contrib.auth.models import User
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
