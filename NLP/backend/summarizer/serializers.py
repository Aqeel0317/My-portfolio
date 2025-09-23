from rest_framework import serializers
from .models import DocumentSummary

class DocumentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentSummary
        fields = '__all__'
