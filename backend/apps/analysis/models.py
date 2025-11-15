from django.db import models
from django.utils import timezone

class Conversation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conversation {self.id} - {self.created_at}"


class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    conversation = models.ForeignKey(
        Conversation, 
        related_name='messages', 
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    text = models.TextField()
    session_number = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.role} - {self.timestamp}"


class AnalysisReport(models.Model):
    conversation = models.OneToOneField(
        Conversation, 
        related_name='report', 
        on_delete=models.CASCADE
    )
    session_count = models.IntegerField()
    questions_asked = models.IntegerField()
    actions_identified = models.IntegerField()
    emotion_results = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report for Conversation {self.conversation.id}"
        