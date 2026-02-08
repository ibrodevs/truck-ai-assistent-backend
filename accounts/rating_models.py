from django.db import models
from accounts.models import UserProfile
from django.core.validators import MinValueValidator, MaxValueValidator


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
        unique_together = ['driver', 'rated_by']  # Один пользователь может оценить водителя только один раз
    
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
