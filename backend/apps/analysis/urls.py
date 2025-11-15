from django.urls import path
from .views import AnalyzeConversationView

urlpatterns = [
    path('analyze/', AnalyzeConversationView.as_view(), name='analyze-conversation'),
]