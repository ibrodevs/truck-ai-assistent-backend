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
]
