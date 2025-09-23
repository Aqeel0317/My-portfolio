# chat/serializers.py
from rest_framework import serializers
from .models import Document, ChatSession, Message

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'file', 'uploaded_at', 'file_type']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'is_user', 'timestamp']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    document = DocumentSerializer(read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'created_at', 'document', 'messages']
