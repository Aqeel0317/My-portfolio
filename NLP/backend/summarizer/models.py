from django.db import models
from django.contrib.auth.models import User

class DocumentSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_text = models.TextField()
    summary_text = models.TextField()
    summary_type = models.CharField(max_length=50)
    highlights = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class TextHighlight(models.Model):
    summary = models.ForeignKey(DocumentSummary, related_name='text_highlights', on_delete=models.CASCADE)
    text = models.TextField()
    color = models.CharField(max_length=50)
    start_index = models.IntegerField()
    end_index = models.IntegerField()
