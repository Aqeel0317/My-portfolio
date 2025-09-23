# chat/utils/ai_service.py
import google.generativeai as genai
from transformers import pipeline
import os

class AIService:
    def __init__(self):
        # Initialize Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize Hugging Face model (using a lightweight model for demo)
        self.hf_pipeline = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-small",
            use_auth_token=os.getenv('HUGGINGFACE_API_KEY')
        )
    
    def generate_response(self, prompt, context=None, use_gemini=True):
        """Generate response using either Gemini or Hugging Face"""
        try:
            if context:
                full_prompt = f"Context from document:\n{context[:2000]}\n\nQuestion: {prompt}\n\nAnswer based on the context provided:"
            else:
                full_prompt = prompt
            
            if use_gemini:
                response = self.gemini_model.generate_content(full_prompt)
                return response.text
            else:
                # Hugging Face response
                response = self.hf_pipeline(
                    full_prompt,
                    max_length=200,
                    num_return_sequences=1,
                    temperature=0.7
                )
                return response[0]['generated_text'][len(full_prompt):].strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"
