from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from .serializers import TranscriptInputSerializer, AnalysisOutputSerializer
from .services import ConversationAnalyzer
from .models import Conversation, Message, AnalysisReport


class AnalyzeConversationView(APIView):
    """
    POST /api/analyze/
    Recibe una transcripción, la almacena, ejecuta análisis y retorna el reporte.
    """
    
    def post(self, request):
        input_serializer = TranscriptInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(
                input_serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transcript_data = input_serializer.validated_data['transcript']
        
        try:
            with transaction.atomic():
                conversation = Conversation.objects.create()
                
                analyzer = ConversationAnalyzer(transcript_data)
                session_numbers = analyzer.get_session_numbers()
                
                messages = []
                for msg_data, session_num in zip(transcript_data, session_numbers):
                    message = Message(
                        conversation=conversation,
                        timestamp=msg_data['timestamp'],
                        role=msg_data['role'],
                        text=msg_data['text'],
                        session_number=session_num
                    )
                    messages.append(message)
                
                Message.objects.bulk_create(messages)
                
                analysis_result = analyzer.analyze()
                
                report = AnalysisReport.objects.create(
                    conversation=conversation,
                    session_count=analysis_result['analysis_summary']['session_count'],
                    questions_asked=analysis_result['analysis_summary']['key_moments']['questions_asked'],
                    actions_identified=analysis_result['analysis_summary']['key_moments']['actions_identified'],
                    emotion_results=analysis_result['analysis_summary']['emotion_analysis_results']
                )
                
                output_serializer = AnalysisOutputSerializer(data=analysis_result)
                output_serializer.is_valid(raise_exception=True)
                
                return Response(
                    output_serializer.data, 
                    status=status.HTTP_201_CREATED
                )
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            