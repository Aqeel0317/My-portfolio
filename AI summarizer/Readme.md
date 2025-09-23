# Document Analysis App

This is a Flask web application that allows users to upload image or PDF files, extract text from them, and then process that text using the **Gemini 1.5 Flash API**. The app is capable of either summarizing the document or answering a specific question based on its content. It utilizes **PyMuPDF** for PDF handling and **PyTesseract** for Optical Character Recognition (OCR), enabling it to handle both digital text and text from scanned documents.

-----

## Features

  - **File Upload**: Supports various image formats (`.png`, `.jpg`, `.jpeg`, `.gif`, etc.) and `.pdf` files.
  - **Intelligent Text Extraction**:
      - For PDFs, it first attempts to extract text directly. If the text is minimal (e.g., from a scanned PDF), it automatically falls back to OCR.
      - For images, it uses OCR by default to get the text.
  - **AI-Powered Processing**:
      - **Summarization**: Generates a concise summary and key points of the extracted text.
      - **Question Answering**: Answers specific questions posed by the user, strictly based on the provided document text.
  - **User-Friendly Interface**: Built with Flask, providing a simple web interface for file uploads and viewing results.

-----

## Technology Stack

  - **Backend**: Python, Flask
  - **AI Model**: Google Gemini 1.5 Flash API
  - **Libraries**:
      - `PyMuPDF` (fitz): For robust PDF parsing and rendering.
      - `Pillow` (PIL): For image processing.
      - `pytesseract`: For Optical Character Recognition (OCR).
      - `python-dotenv`: To manage environment variables securely.
      - `google-generativeai`: Python client for the Gemini API.

-----

## Prerequisites

Before running the application, you must have the following installed:

  - **Python 3.7+**

  - **Tesseract OCR Engine**: This is a standalone executable that must be installed on your system.

      - **Windows**: Download from the [Tesseract-OCR GitHub](https://www.google.com/search?q=https://github.com/UB-Mannheim/tesseract/wiki).
      - **Linux (Ubuntu/Debian)**: `sudo apt-get update && sudo apt-get install tesseract-ocr`
      - **macOS**: `brew install tesseract`

    After installation, you may need to configure the path to the Tesseract executable in the `app.py` file if it's not in your system's PATH.

  - **Google API Key**: You'll need an API key for the Gemini API. You can get one from the [Google AI for Developers](https://aistudio.google.com/app/apikey) website.

-----

## Setup and Installation

1.  **Clone the repository:**

    ```
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Create a virtual environment** (recommended):

    ```
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies**:

    ```
    pip install -r requirements.txt
    ```

    > **Note**: `requirements.txt` should contain the list of libraries used, such as `Flask`, `PyMuPDF`, `Pillow`, `pytesseract`, `python-dotenv`, and `google-generativeai`.

4.  **Configure environment variables**:
    Create a `.env` file in the project's root directory and add your Google API key and a secret key for Flask:

    ```
    GOOGLE_API_KEY="your_google_api_key_here"
    FLASK_SECRET_KEY="a_strong_random_secret_key"
    ```

5.  **Run the application**:

    ```
    python app.py
    ```

6.  **Access the app**:
    Open your web browser and navigate to `http://127.0.0.1:5000`.

-----

## Usage

1.  Go to the "Upload" page.
2.  Select an image or PDF file.
3.  (Optional) Enter a specific question you want answered from the document.
4.  Click "Process".
5.  The application will display the extracted text and the AI-generated response.