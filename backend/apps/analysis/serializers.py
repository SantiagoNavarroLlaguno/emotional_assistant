from rest_framework import serializers
from .models import Conversation, Message, AnalysisReport


class MessageInputSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    role = serializers.ChoiceField(choices=['user', 'assistant'])
    text = serializers.CharField()


class TranscriptInputSerializer(serializers.Serializer):
    transcript = MessageInputSerializer(many=True)
    
    def validate_transcript(self, value):
        if not value:
            raise serializers.ValidationError("Transcript cannot be empty")
        return value


class KeyMomentsSerializer(serializers.Serializer):
    questions_asked = serializers.IntegerField()
    actions_identified = serializers.IntegerField()


class EmotionResultSerializer(serializers.Serializer):
    emotion = serializers.CharField()


class AnalysisSummarySerializer(serializers.Serializer):
    session_count = serializers.IntegerField()
    key_moments = KeyMomentsSerializer()
    emotion_analysis_results = EmotionResultSerializer(many=True)


class AnalysisOutputSerializer(serializers.Serializer):
    analysis_summary = AnalysisSummarySerializer()
    