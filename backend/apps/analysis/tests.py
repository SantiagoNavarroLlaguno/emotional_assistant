from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, timedelta
from .models import Conversation, Message, AnalysisReport
from .services import ConversationAnalyzer


class ConversationAnalyzerTests(TestCase):
    
    def test_session_count_single_session(self):
        """Test que una conversación continua cuenta como 1 sesión"""
        transcript = [
            {"timestamp": "2025-10-27T10:00:00Z", "role": "assistant", "text": "Hola"},
            {"timestamp": "2025-10-27T10:05:00Z", "role": "user", "text": "Hola"},
            {"timestamp": "2025-10-27T10:08:00Z", "role": "assistant", "text": "¿Cómo estás?"},
        ]
        analyzer = ConversationAnalyzer(transcript)
        result = analyzer.analyze()
        self.assertEqual(result['analysis_summary']['session_count'], 1)
    
    def test_session_count_multiple_sessions(self):
        """Test que silencios de 10+ minutos crean nuevas sesiones"""
        transcript = [
            {"timestamp": "2025-10-27T10:00:00Z", "role": "assistant", "text": "Hola"},
            {"timestamp": "2025-10-27T10:05:00Z", "role": "user", "text": "Hola"},
            {"timestamp": "2025-10-27T10:16:00Z", "role": "assistant", "text": "¿Sigues ahí?"},
            {"timestamp": "2025-10-27T10:17:00Z", "role": "user", "text": "Sí"},
        ]
        analyzer = ConversationAnalyzer(transcript)
        result = analyzer.analyze()
        self.assertEqual(result['analysis_summary']['session_count'], 2)
    
    def test_question_counting(self):
        """Test que cuenta correctamente mensajes con '?'"""
        transcript = [
            {"timestamp": "2025-10-27T10:00:00Z", "role": "assistant", "text": "Hola"},
            {"timestamp": "2025-10-27T10:05:00Z", "role": "user", "text": "¿Cómo estás?"},
            {"timestamp": "2025-10-27T10:08:00Z", "role": "assistant", "text": "¿Y tú?"},
        ]
        analyzer = ConversationAnalyzer(transcript)
        result = analyzer.analyze()
        self.assertEqual(result['analysis_summary']['key_moments']['questions_asked'], 2)
    
    def test_action_keyword_counting(self):
        """Test que identifica palabras clave de acción"""
        transcript = [
            {"timestamp": "2025-10-27T10:00:00Z", "role": "user", "text": "Necesito ayuda"},
            {"timestamp": "2025-10-27T10:05:00Z", "role": "user", "text": "Podrías ayudarme"},
            {"timestamp": "2025-10-27T10:08:00Z", "role": "assistant", "text": "Claro"},
            {"timestamp": "2025-10-27T10:10:00Z", "role": "user", "text": "Tengo una tarea"},
        ]
        analyzer = ConversationAnalyzer(transcript)
        result = analyzer.analyze()
        self.assertEqual(result['analysis_summary']['key_moments']['actions_identified'], 3)
    
    def test_emotion_analysis_runs(self):
        """Test que el análisis emocional retorna resultados"""
        transcript = [
            {"timestamp": "2025-10-27T10:00:00Z", "role": "user", 
             "text": "Me siento muy triste hoy porque las cosas no van bien en mi vida y necesito hablar con alguien sobre esto"},
        ]
        analyzer = ConversationAnalyzer(transcript)
        result = analyzer.analyze()
        self.assertGreater(len(result['analysis_summary']['emotion_analysis_results']), 0)


class AnalyzeAPITests(APITestCase):
    
    def setUp(self):
        self.url = reverse('analyze-conversation')
        self.valid_payload = {
            "transcript": [
                {
                    "timestamp": "2025-10-27T10:00:00Z",
                    "role": "assistant",
                    "text": "Hola, ¿cómo te sientes hoy?"
                },
                {
                    "timestamp": "2025-10-27T10:15:30Z",
                    "role": "user",
                    "text": "Me siento bien, gracias por preguntar"
                }
            ]
        }
    
    def test_create_analysis_success(self):
        """Test que el endpoint crea análisis correctamente"""
        response = self.client.post(self.url, self.valid_payload, format='json')

        if response.status_code == 500:
            print(response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('analysis_summary', response.data)
        self.assertIn('session_count', response.data['analysis_summary'])
    
    def test_creates_database_records(self):
        """Test que se crean registros en la base de datos"""
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(AnalysisReport.objects.count(), 1)
    
    def test_empty_transcript_fails(self):
        """Test que transcript vacío retorna error"""
        payload = {"transcript": []}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_role_fails(self):
        """Test que rol inválido retorna error"""
        payload = {
            "transcript": [
                {
                    "timestamp": "2025-10-27T10:00:00Z",
                    "role": "invalid_role",
                    "text": "Test"
                }
            ]
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
