# chat/utils/document_parser.py
import PyPDF2
from docx import Document as DocxDocument
import io

class DocumentParser:
    @staticmethod
    def parse_pdf(file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    @staticmethod
    def parse_docx(file):
        """Extract text from DOCX file"""
        try:
            doc = DocxDocument(file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")
    
    @staticmethod
    def parse_document(file, file_type):
        """Parse document based on file type"""
        if file_type.lower() == 'pdf':
            return DocumentParser.parse_pdf(file)
        elif file_type.lower() in ['docx', 'doc']:
            return DocumentParser.parse_docx(file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
