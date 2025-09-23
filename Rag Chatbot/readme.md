
# Document-Based AI Chat API 💬

This is a RESTful API built with Django and Django REST Framework that enables users to have an intelligent conversation with an AI model based on the content of an uploaded document. It provides endpoints for uploading documents, creating chat sessions, sending messages, and retrieving session history.

-----

## Features ✨

  * **Document Upload & Parsing**: Supports uploading PDF and Word (`.docx`, `.doc`) documents. The API extracts the text content to be used as context for the AI.
  * **Context-Aware Chat**: When a document is uploaded, a chat session is created. Subsequent messages sent within that session use the document's content as a knowledge base for the AI's responses.
  * **Dynamic AI Integration**: The application is built with a flexible `AIService` layer, making it easy to integrate with different AI models. The current implementation can use a model like Google Gemini to generate responses.
  * **Stateless & Scalable**: The API is stateless, managing sessions and message history via a database, which allows for horizontal scaling.
  * **Clear API Endpoints**: Provides a well-defined set of endpoints for a full chat flow: `upload`, `create session`, `send message`, `get session history`, and `delete session`.

-----

## Technology Stack 💻

  * **Backend**: Python, Django, Django REST Framework
  * **AI Service**: `google-generativeai` (can be configured for other services)
  * **Database**: SQLite (default), but can be configured for PostgreSQL or MySQL
  * **Document Parsing Libraries**:
      * `PyPDF2` (for PDF files)
      * `python-docx` (for `.docx` files)
  * **Data Serialization**: `rest_framework` serializers

-----

## Prerequisites ⚙️

  * **Python 3.8+**
  * A **Google Gemini API Key** (or another API key if a different AI service is configured).
  * The required Python libraries.

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

3.  **Install the required Python packages**:

    ```bash
    pip install Django djangorestframework PyPDF2 python-docx google-generativeai
    ```

    (Note: You might need to install `pydocx` if `.doc` parsing is required, as `python-docx` is for `.docx`).

4.  **Configure your API Key**:
    It is **highly recommended** to store your API key in an environment variable. Create a `.env` file in your project root and add your key:

    ```
    GEMINI_API_KEY="your_gemini_api_key_here"
    ```

    Then, modify `chat/utils/ai_service.py` to load this key.

5.  **Run Migrations**:

    ```bash
    python manage.py migrate
    ```

6.  **Start the Django development server**:

    ```bash
    python manage.py runserver
    ```

7.  The API will be available at `http://127.0.0.1:8000/`.

-----

## API Endpoints 🌐

The following endpoints are available. All endpoints are accessible at `http://127.0.0.1:8000/api/chat/`.

### 1\. Upload a Document and Start a Session

  * **Endpoint**: `/upload/`
  * **Method**: `POST`
  * **Description**: Upload a document to start a new chat session with its content as the context.
  * **Request Body**: `multipart/form-data` with a `file` field.

### 2\. Create a Blank Chat Session

  * **Endpoint**: `/sessions/create/`
  * **Method**: `POST`
  * **Description**: Creates a new chat session without a document. Good for general conversation.

### 3\. Send a Message to a Session

  * **Endpoint**: `/sessions/<int:session_id>/message/`
  * **Method**: `POST`
  * **Description**: Sends a user message to the specified session and receives an AI response.
  * **Request Body**: `{"message": "Your question here.", "use_gemini": true}`

### 4\. Get Chat Session History

  * **Endpoint**: `/sessions/<int:session_id>/`
  * **Method**: `GET`
  * **Description**: Retrieves all messages associated with a specific chat session.

### 5\. List All Chat Sessions

  * **Endpoint**: `/sessions/`
  * **Method**: `GET`
  * **Description**: Returns a list of all active chat sessions.

### 6\. Delete a Chat Session

  * **Endpoint**: `/sessions/<int:session_id>/`
  * **Method**: `DELETE`
  * **Description**: Deletes a chat session and all its associated messages.