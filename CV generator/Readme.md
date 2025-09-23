# Online CV Generator

This is a Flask-based web application that allows users to easily create and generate a professional CV. Users can input their personal information, experience, education, and skills, upload a profile picture, and then choose from a selection of pre-designed templates to generate their CV as a viewable HTML page.

-----

## Features

  - **Web-based Form**: A simple, dynamic form for entering all the necessary CV details.
  - **Profile Picture Upload**: Supports uploading a profile photo which is then displayed on the generated CV.
  - **Multiple Templates**: A selection of different CV layouts and designs (e.g., Classic, Modern, Two-Column) to choose from.
  - **Dynamic Content**: The form supports adding multiple entries for skills, work experience, and education.
  - **HTML Output**: Generates a clean, print-friendly HTML page of the CV, ready to be saved as a PDF from the browser.
  - **Session Management**: Uses Flask sessions to temporarily store user data between form submission and template selection.
  - **Secure File Handling**: Uses `werkzeug.utils.secure_filename` to prevent directory traversal attacks on uploaded files.

-----

## Technology Stack

  - **Backend**: Python, Flask
  - **Frontend**: HTML, CSS
  - **Libraries**:
      - `Flask`: The web framework.
      - `werkzeug`: For secure file uploads.
      - `Pillow` (PIL): While not explicitly imported in the provided code, it's a common dependency for image processing and is a good practice to include in the `requirements.txt` for image-related tasks.
      - `uuid`: For generating unique filenames.
      - `base64`: To embed the profile picture directly into the HTML for a self-contained page.

-----

## Prerequisites

  - **Python 3.6+**
  - **Required Python libraries**: All are listed in the `requirements.txt` file (see Installation).

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

4.  **Create an `uploads` folder**:
    The application is configured to store uploaded images in an `uploads` directory. Make sure this folder exists in the root of your project. The provided code automatically creates it, but it's good to be aware of its purpose.

5.  **Configure environment variables**:
    Create a `.env` file in the project's root directory to store your secret key for Flask sessions.

    ```
    FLASK_SECRET_KEY="your_secret_key_here"
    ```

    > **Note**: For production, use a long, random string for the `FLASK_SECRET_KEY`.

6.  **Run the application**:

    ```
    python app.py
    ```

7.  **Access the app**:
    Open your web browser and navigate to `http://127.0.0.1:5000`.

-----

## Usage

1.  Navigate to the homepage (`/`) to fill out the CV form.
2.  Enter all your details, and select a profile picture to upload.
3.  Click "Process" to submit the form.
4.  You will be redirected to a template selection page. Choose a template that suits your style.
5.  The final CV will be rendered as a new HTML page in your browser. From here, you can use your browser's "Print to PDF" function to save the CV as a file.