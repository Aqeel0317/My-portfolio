import os
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import PyPDF2
import docx
import google.generativeai as genai

# Configure logging
logger = logging.getLogger(__name__)

class DocumentUploadView(APIView):
    def post(self, request):
        # Logging for debugging
        logger.info("Document upload request received")

        # Detailed file validation
        file = request.FILES.get('file')
        if not file:
            logger.error("No file uploaded")
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        # File size validation
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            logger.error(f"File too large: {file.size} bytes")
            return Response({'error': 'File size exceeds 10MB limit'}, status=status.HTTP_400_BAD_REQUEST)
        
        # File type validation
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in allowed_extensions:
            logger.error(f"Unsupported file type: {file_extension}")
            return Response({'error': 'Unsupported file type'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            text = self._extract_text(file)
            logger.info(f"Text extracted. Length: {len(text)} characters")
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            return Response({'error': f'Text extraction failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Gemini summarization logic
        try:
            # Ensure API key is set
            GEMINI_API_KEY = 'AIzaSyCarDqHPIMgg-tCGx9itHkU5zCQ9Zxtsg8'  # Replace with your actual key
            if not GEMINI_API_KEY:
                raise ValueError("Gemini API key is not set")
            
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            summary_type = request.data.get('summary_type', 'tldr')
            prompt = self._get_prompt(summary_type, text)
            
            response = model.generate_content(prompt)
            
            return Response({
                'original_text': text[:500] + '...' if len(text) > 500 else text,
                'summary': response.text,
                'summary_type': summary_type
            })
        
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return Response({'error': f'Summarization failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _extract_text(self, file):
        filename = file.name.lower()
        
        if filename.endswith('.pdf'):
            return self._extract_pdf_text(file)
        elif filename.endswith('.docx'):
            return self._extract_docx_text(file)
        elif filename.endswith('.txt'):
            return file.read().decode('utf-8')
        else:
            raise ValueError('Unsupported file type')
    
    def _extract_pdf_text(self, file):
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def _extract_docx_text(self, file):
        doc = docx.Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])
    
    def _get_prompt(self, summary_type, text):
        # Truncate text if it's too long to prevent API errors
        max_text_length = 5000
        truncated_text = text[:max_text_length]
        
        prompts = {
            'tldr': f"Provide a very concise TL;DR summary of the following text (max 100 words): {truncated_text}",
            'bullet': f"Create a bullet point summary of the following text: {truncated_text}",
            'executive': f"Create an executive-style summary of the following text: {truncated_text}"
        }
        return prompts.get(summary_type, prompts['tldr'])

class TextAnalysisView(APIView):
    def post(self, request):
        text = request.data.get('text', '')
        
        if not text:
            return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Basic text analysis
        words = text.split()
        sentences = text.split('.')
        
        metrics = {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': round(sum(len(word) for word in words) / len(words), 2) if words else 0,
            'entities': self._extract_basic_entities(text)
        }
        
        return Response(metrics)
    
    def _extract_basic_entities(self, text):
        # Very basic entity extraction (can be replaced with more advanced NLP)
        import re
        
        entities = {
            'persons': re.findall(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', text)[:5],
            'organizations': re.findall(r'\b([A-Z][a-z]+ (Company|Inc\.|Corporation|LLC))\b', text)[:5],
            'locations': re.findall(r'\b([A-Z][a-z]+ (City|State|Country|Region))\b', text)[:5]
        }
        
        return entities
