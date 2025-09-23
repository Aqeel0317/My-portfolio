# chat/views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Document, ChatSession, Message
from .serializers import ChatSessionSerializer, MessageSerializer
from .utils.document_parser import DocumentParser
from .utils.ai_service import AIService
import os

ai_service = AIService()

@api_view(['POST'])
def upload_document(request):
    """Upload and parse a document"""
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    file_extension = file.name.split('.')[-1].lower()
    
    if file_extension not in ['pdf', 'docx', 'doc']:
        return Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Parse document content
        content = DocumentParser.parse_document(file, file_extension)
        
        # Save document
        document = Document.objects.create(
            file=file,
            content=content,
            file_type=file_extension
        )
        
        # Create new chat session with this document
        session = ChatSession.objects.create(document=document)
        
        return Response({
            'session_id': session.id,
            'document_id': document.id,
            'content_preview': content[:500] + '...' if len(content) > 500 else content
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_session(request):
    """Create a new chat session without document"""
    session = ChatSession.objects.create()
    return Response({'session_id': session.id}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def send_message(request, session_id):
    """Send a message and get AI response"""
    session = get_object_or_404(ChatSession, id=session_id)
    user_message = request.data.get('message', '')
    use_gemini = request.data.get('use_gemini', True)
    
    if not user_message:
        return Response({'error': 'No message provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Save user message
    user_msg = Message.objects.create(
        session=session,
        content=user_message,
        is_user=True
    )
    
    # Get context from document if available
    context = None
    if session.document:
        context = session.document.content
    
    # Generate AI response
    ai_response = ai_service.generate_response(user_message, context, use_gemini)
    
    # Save AI response
    ai_msg = Message.objects.create(
        session=session,
        content=ai_response,
        is_user=False
    )
    
    return Response({
        'user_message': MessageSerializer(user_msg).data,
        'ai_response': MessageSerializer(ai_msg).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_session(request, session_id):
    """Get session with all messages"""
    session = get_object_or_404(ChatSession, id=session_id)
    serializer = ChatSessionSerializer(session)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_session(request, session_id):
    """Delete a chat session"""
    session = get_object_or_404(ChatSession, id=session_id)
    session.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def list_sessions(request):
    """List all chat sessions"""
    sessions = ChatSession.objects.all().order_by('-created_at')
    serializer = ChatSessionSerializer(sessions, many=True)
    return Response(serializer.data)
