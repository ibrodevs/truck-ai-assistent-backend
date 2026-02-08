from django.urls import path
from . import views

urlpatterns = [
    path('csrf/', views.csrf_token_view, name='csrf-token'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_view, name='update-profile'),
    path('check-auth/', views.check_auth, name='check-auth'),
    
    # Календарь доступности
    path('availability/', views.availability_list_view, name='availability-list'),
    path('availability/create/', views.availability_create_view, name='availability-create'),
    path('availability/<int:pk>/update/', views.availability_update_view, name='availability-update'),
    path('availability/<int:pk>/delete/', views.availability_delete_view, name='availability-delete'),
    
    # Рейтинги водителей
    path('ratings/', views.driver_ratings_list_view, name='ratings-list'),
    path('ratings/driver/<int:driver_id>/', views.driver_ratings_list_view, name='driver-ratings'),
    path('ratings/driver/<int:driver_id>/average/', views.driver_average_rating_view, name='driver-average-rating'),
    path('ratings/create/', views.driver_rating_create_view, name='rating-create'),
    path('ratings/<int:pk>/update/', views.driver_rating_update_view, name='rating-update'),
    path('ratings/<int:pk>/delete/', views.driver_rating_delete_view, name='rating-delete'),
    
    # Список водителей
    path('drivers/', views.drivers_list_view, name='drivers-list'),
    path('drivers/<int:driver_id>/', views.driver_detail_view, name='driver-detail'),
]