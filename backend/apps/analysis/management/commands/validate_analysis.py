from django.core.management.base import BaseCommand
from apps.analysis.models import Conversation, Message, AnalysisReport


class Command(BaseCommand):
    help = 'Valida el análisis de una conversación para revisión por psicólogos'

    def add_arguments(self, parser):
        parser.add_argument('conversation_id', type=int, help='ID de la conversación')

    def handle(self, *args, **options):
        conversation_id = options['conversation_id']
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            report = conversation.report
            messages = conversation.messages.all()
            
            self.stdout.write(self.style.SUCCESS(f'\n=== Análisis de Conversación #{conversation_id} ===\n'))
            
            # Transcripción completa
            self.stdout.write(self.style.WARNING('TRANSCRIPCIÓN:'))
            for msg in messages:
                self.stdout.write(f'[Sesión {msg.session_number}] {msg.timestamp} - {msg.role.upper()}:')
                self.stdout.write(f'  {msg.text}\n')
            
            # Resumen del análisis
            self.stdout.write(self.style.WARNING('\nRESUMEN DEL ANÁLISIS:'))
            self.stdout.write(f'Total de sesiones detectadas: {report.session_count}')
            self.stdout.write(f'Preguntas identificadas: {report.questions_asked}')
            self.stdout.write(f'Acciones identificadas: {report.actions_identified}')
            
            # Preguntas encontradas
            self.stdout.write(self.style.WARNING('\nPREGUNTAS ENCONTRADAS:'))
            for msg in messages.filter(text__contains='?'):
                self.stdout.write(f'  • {msg.text}')
            
            # Acciones encontradas
            action_keywords = ["necesito", "podrías", "ayúdame", "tarea", "hacer"]
            self.stdout.write(self.style.WARNING('\nACCIONES IDENTIFICADAS:'))
            for msg in messages:
                if any(keyword in msg.text.lower() for keyword in action_keywords):
                    self.stdout.write(f'  • {msg.text}')
            
            # Emociones
            self.stdout.write(self.style.WARNING('\nEMOCIONES DETECTADAS:'))
            for emotion in report.emotion_results:
                self.stdout.write(f'  • {emotion["emotion"]}')
            
            self.stdout.write(self.style.SUCCESS('\n✓ Validación completada\n'))
            
        except Conversation.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Conversación #{conversation_id} no encontrada'))
            