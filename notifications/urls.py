from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list_view, name='notifications-list'),
    path('unread-count/', views.notifications_unread_count_view, name='notifications-unread-count'),
    path('<int:pk>/mark-read/', views.notification_mark_read_view, name='notification-mark-read'),
    path('mark-all-read/', views.notification_mark_all_read_view, name='notification-mark-all-read'),
    path('<int:pk>/delete/', views.notification_delete_view, name='notification-delete'),
    path('create/', views.notification_create_view, name='notification-create'),
]
