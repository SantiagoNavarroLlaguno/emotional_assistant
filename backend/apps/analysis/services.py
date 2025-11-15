import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from django.utils.dateparse import parse_datetime


def get_emotion_from_ai(text_block: str) -> List[str]:
    """Simula una llamada a una API de IA costosa."""
    if len(text_block) < 20:
        return ["error: text too short"]
    emotions = ["Disgust", "Rage", "Happiness", "Sadness", "Surprise", "Fear"]
    return random.choices(emotions, k=random.randint(1, 3))


class ConversationAnalyzer:
    SESSION_TIMEOUT_MINUTES = 10
    MIN_TEXT_LENGTH_FOR_AI = 100
    ACTION_KEYWORDS = ["necesito", "podrías", "ayúdame", "tarea", "hacer"]
    
    def __init__(self, transcript_data: List[Dict[str, Any]]):
        self.transcript_data = sorted(
            transcript_data, 
            key=lambda x: x['timestamp'] if isinstance(x['timestamp'], datetime) else parse_datetime(x['timestamp'])
    )
    
    def analyze(self) -> Dict[str, Any]:
        """Ejecuta el análisis completo de la conversación."""
        session_count = self._count_sessions()
        questions_asked = self._count_questions()
        actions_identified = self._count_actions()
        emotion_results = self._analyze_emotions()
        
        return {
            "analysis_summary": {
                "session_count": session_count,
                "key_moments": {
                    "questions_asked": questions_asked,
                    "actions_identified": actions_identified
                },
                "emotion_analysis_results": emotion_results
            }
        }
    
    def _count_sessions(self) -> int:
        """Cuenta el número de sesiones basado en silencios de 10+ minutos."""
        if not self.transcript_data:
            return 0
        
        session_count = 1
        for i in range(1, len(self.transcript_data)):
            prev_time = self.transcript_data[i-1]['timestamp']
            curr_time = self.transcript_data[i]['timestamp']
            
            if isinstance(prev_time, str):
                prev_time = parse_datetime(prev_time)
            if isinstance(curr_time, str):
                curr_time = parse_datetime(curr_time)
            
            time_diff = curr_time - prev_time
            if time_diff > timedelta(minutes=self.SESSION_TIMEOUT_MINUTES):
                session_count += 1
        
        return session_count
    
    def get_session_numbers(self) -> List[int]:
        """Retorna el número de sesión para cada mensaje."""
        if not self.transcript_data:
            return []
        
        session_numbers = [1]
        current_session = 1
        
        for i in range(1, len(self.transcript_data)):
            prev_time = self.transcript_data[i-1]['timestamp']
            curr_time = self.transcript_data[i]['timestamp']
            
            if isinstance(prev_time, str):
                prev_time = parse_datetime(prev_time)
            if isinstance(curr_time, str):
                curr_time = parse_datetime(curr_time)
            
            time_diff = curr_time - prev_time
            if time_diff > timedelta(minutes=self.SESSION_TIMEOUT_MINUTES):
                current_session += 1
            
            session_numbers.append(current_session)
        
        return session_numbers
    
    def _count_questions(self) -> int:
        """Cuenta mensajes que contienen '?'."""
        return sum(1 for msg in self.transcript_data if '?' in msg['text'])
    
    def _count_actions(self) -> int:
        """Cuenta mensajes con palabras clave de acción."""
        count = 0
        for msg in self.transcript_data:
            text_lower = msg['text'].lower()
            if any(keyword in text_lower for keyword in self.ACTION_KEYWORDS):
                count += 1
        return count
    
    def _analyze_emotions(self) -> List[Dict[str, Any]]:
        """Analiza emociones agrupando mensajes en bloques de 100+ caracteres."""
        emotion_results = []
        current_block = ""
        
        for msg in self.transcript_data:
            current_block += " " + msg['text']
            
            if len(current_block) >= self.MIN_TEXT_LENGTH_FOR_AI:
                emotions = get_emotion_from_ai(current_block.strip())
                for emotion in emotions:
                    emotion_results.append({"emotion": emotion})
                current_block = ""
        
        # Procesar el bloque restante si existe
        if current_block.strip() and len(current_block.strip()) >= 20:
            emotions = get_emotion_from_ai(current_block.strip())
            for emotion in emotions:
                emotion_results.append({"emotion": emotion})
        
        return emotion_results
        