from django.urls import path
from . import views
from . import analytics_views

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:conversation_id>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('send-message/', views.send_message, name='send-message'),
    path('driver-matching/', views.driver_matching, name='driver-matching'),
    path('driver-matching/history/', views.driver_matching_history, name='driver-matching-history'),
    path('assistant-types/', views.assistant_types, name='assistant-types'),
    
    # Analytics endpoints
    path('analytics/overview/', analytics_views.analytics_overview_view, name='analytics-overview'),
    path('analytics/activity/', analytics_views.analytics_activity_view, name='analytics-activity'),
    path('analytics/admin/', analytics_views.analytics_admin_view, name='analytics-admin'),
]