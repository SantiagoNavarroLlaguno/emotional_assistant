from django.contrib import admin
from .models import Conversation, Message, AnalysisReport


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'message_count')
    list_filter = ('created_at',)
    search_fields = ('id',)
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'timestamp', 'role', 'session_number', 'text_preview')
    list_filter = ('role', 'session_number', 'timestamp')
    search_fields = ('text',)
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'


@admin.register(AnalysisReport)
class AnalysisReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'session_count', 'questions_asked', 
                    'actions_identified', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('emotion_results',)
    