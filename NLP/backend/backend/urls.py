from django.urls import path
from summarizer.views import DocumentUploadView, TextAnalysisView

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('api/analyze/', TextAnalysisView.as_view(), name='text_analysis'),
]
