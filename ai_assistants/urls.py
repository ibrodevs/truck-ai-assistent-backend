from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:conversation_id>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('send-message/', views.send_message, name='send-message'),
    path('driver-matching/', views.driver_matching, name='driver-matching'),
    path('driver-matching/history/', views.driver_matching_history, name='driver-matching-history'),
    path('assistant-types/', views.assistant_types, name='assistant-types'),
]