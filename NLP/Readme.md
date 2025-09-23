
# Document Analysis API 📝

This is a **RESTful API** built with Django REST Framework that provides endpoints for **document analysis and summarization**. It allows users to upload various document types (PDF, DOCX, TXT), extracts the text, and then uses the **Google Gemini API** to generate different types of summaries. The API also includes a basic endpoint for simple text analysis, such as word count and entity extraction.

-----

## Features ✨

  * **Document Upload**: Securely handles file uploads with validation for file type and size (up to 10MB).
  * **Text Extraction**: Extracts plain text from `.pdf`, `.docx`, and `.txt` files.
  * **AI-Powered Summarization**: Integrates with the Google Gemini API to produce summaries in different styles:
      * **`tldr`**: A very brief, concise summary.
      * **`bullet`**: A summary presented in a list of key points.
      * **`executive`**: A more formal, detailed summary suitable for business contexts.
  * **Basic Text Analysis**: An endpoint for analyzing provided text, reporting metrics like word count, sentence count, average word length, and basic entity recognition.
  * **Robust Error Handling**: Provides clear and informative error responses for common issues like unsupported file types, oversized files, or API failures.

-----

## Technology Stack 💻

  * **Backend**: Python, Django REST Framework
  * **AI Model**: Google Gemini 1.5 Flash
  * **Libraries**:
      * `djangorestframework`: For building the API.
      * `PyPDF2`: For reading text from PDF files.
      * `python-docx`: For extracting text from Word documents.
      * `google-generativeai`: The official Python client for the Gemini API.
  * **Logging**: `logging` module for tracking requests and errors.

-----

## Prerequisites ⚙️

To run this API locally, you will need:

  * **Python 3.8+**
  * A **Google Gemini API Key**. You can obtain one for free from the [Google AI Studio](https://aistudio.google.com/app/apikey).
  * The required Python libraries listed in the `requirements.txt` file.

-----

## Setup and Installation 🚀

1.  **Clone the repository**:

    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

    > `requirements.txt` should contain: `Django`, `djangorestframework`, `PyPDF2`, `python-docx`, `google-generativeai`.

4.  **Configure your Gemini API Key**:
    Replace the placeholder `'AIzaSyCarDqHPIMgg-tCGx9itHkU5zCQ9Zxtsg8'` in the `DocumentUploadView` class with your actual API key. For production, it's highly recommended to use environment variables instead of hard-coding the key.

    ```python
    # In DocumentUploadView
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_actual_key_here") 
    ```

5.  **Run the Django development server**:

    ```bash
    python manage.py runserver
    ```

6.  The API will be available at `http://127.0.0.1:8000/`.

-----

## API Endpoints 🌐

### 1\. Document Upload and Summarization

  * **Endpoint**: `/api/upload/`

  * **Method**: `POST`

  * **Description**: Accepts a document file, extracts its text, and returns an AI-generated summary.

  * **Request Body**:

      * `file` (multipart/form-data): The document file (`.pdf`, `.docx`, or `.txt`).
      * `summary_type` (string, optional): The type of summary to generate. Valid values are `tldr`, `bullet`, or `executive`. Defaults to `tldr`.

  * **Example Request (using `curl`)**:

    ```bash
    curl -X POST -F "file=@/path/to/your/document.pdf" -F "summary_type=bullet" http://127.0.0.1:8000/api/upload/
    ```

  * **Example Response**:

    ```json
    {
      "original_text": "The quick brown fox jumps over the lazy dog...",
      "summary": "- The fox is quick and brown.\n- It jumps over a lazy dog.",
      "summary_type": "bullet"
    }
    ```

### 2\. Text Analysis

  * **Endpoint**: `/api/analyze/`

  * **Method**: `POST`

  * **Description**: Accepts a block of text and returns basic analysis metrics.

  * **Request Body**:

      * `text` (string): The text to analyze.

  * **Example Request (using `curl`)**:

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"text": "John Doe works at Google in California."}' http://127.0.0.1:8000/api/analyze/
    ```

  * **Example Response**:

    ```json
    {
      "word_count": 8,
      "sentence_count": 2,
      "avg_word_length": 4.5,
      "entities": {
        "persons": ["John Doe"],
        "organizations": ["Google"],
        "locations": ["California"]
      }
    }
    ```