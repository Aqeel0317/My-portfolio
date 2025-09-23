# chat/models.py
from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    file_type = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.file.name} - {self.uploaded_at}"

class ChatSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Session {self.id} - {self.created_at}"

class Message(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{'User' if self.is_user else 'Bot'}: {self.content[:50]}..."
