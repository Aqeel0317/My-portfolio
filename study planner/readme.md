# Student Success Platform

This Flask application is a comprehensive platform designed to help students manage their academic life. It combines goal tracking, AI-powered study assistance, and a reminder system to create a personalized and effective learning environment. The application utilizes a local SQLite database for data storage and integrates with external APIs like **Google Gemini** for AI capabilities and **Hugging Face** for image generation.

-----

## Features ✨

  * **Goal Tracking**: Set, track, and manage academic goals with target dates.
  * **AI Progress Analysis**: An AI model automatically analyzes progress updates and estimates a completion percentage for each goal.
  * **Study Coach Chatbot**: A personalized chatbot provides encouraging and actionable advice based on a student's active goals and recent progress.
  * **AI-Generated Study Notes**: Automatically generate comprehensive study notes on any topic, complete with an AI-generated educational image.
  * **Image Generation**: Create visual aids for study notes or other purposes using a text-to-image model.
  * **PDF Export**: Export study notes as a professional PDF document.
  * **Automated Reminders**: Set up email reminders for goals to stay on track.
  * **CRUD Functionality**: Full Create, Read, Update, and Delete support for goals, progress entries, study notes, and reminders.

-----

## Prerequisites ⚙️

  * **Python 3.7+**
  * **pip** (Python package installer)
  * **A Google Gemini API Key**
  * **A Hugging Face API Key**
  * **An Email Account (e.g., Gmail)** for sending reminders. You may need to enable "less secure app access" or generate an application-specific password.

-----

## Setup and Installation 🚀

1.  **Clone the repository or save the code**: Save the provided Python code as `app.py`.
2.  **Set up API Keys and Email Credentials**:
      * Set the following environment variables with your keys and credentials:
        ```bash
        export GEMINI_API_KEY='your_gemini_api_key_here'
        export HF_API_KEY='your_huggingface_api_key_here'
        export EMAIL_USER='your_email_address@gmail.com'
        export EMAIL_PASSWORD='your_email_password_or_app_password'
        ```
      * For Windows, use `set` instead of `export`.
3.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    ```
4.  **Activate the virtual environment**:
      * **On Windows**: `venv\Scripts\activate`
      * **On macOS/Linux**: `source venv/bin/activate`
5.  **Install the dependencies**:
    ```bash
    pip install Flask Flask-SQLAlchemy google-generativeai requests apscheduler reportlab
    ```
6.  **Create the required directories**: The app automatically creates a `static/images` directory to store generated images, but it's good practice to ensure the `templates` folder exists.
7.  **Run the application**:
    ```bash
    python app.py
    ```
8.  **Access the application**: Open your web browser and go to `http://127.0.0.1:5000`.

-----

## Usage Guide 📖

### **Goals**

  * **Add a Goal**: Define a new academic goal with a title, description, and target date.
  * **Track Progress**: For each goal, you can add a new progress entry describing your latest work. The AI will analyze your entry and estimate your progress percentage.
  * **Set Reminders**: Link a reminder to a goal with a specific date, time, and email address to receive an automated email notification.

### **Study Notes**

  * **Generate Notes**: Go to the Notes page and enter a topic (e.g., "Photosynthesis"). The AI will generate detailed study notes and a relevant image.
  * **Export Notes**: View and export any saved note as a PDF for offline studying.

### **AI Chatbot**

  * **Get Coaching**: Use the chat interface to talk to your AI study coach. The coach uses your goals and progress to provide personalized and motivating advice.

### **Image Generation**

  * **Create Images**: On the Images page, enter a prompt (e.g., "A diagram of the solar system") to generate an educational image. This is a great way to create custom visual aids for your notes.

-----

## Project Structure 📂

```
.
├── app.py                  # The main Flask application file
├── venv/                   # Python virtual environment
├── static/
│   └── images/             # Stores AI-generated images
└── templates/              # All HTML templates
    ├── index.html
    ├── goals.html
    ├── add_goal.html
    ├── view_goal.html
    ├── chat.html
    ├── notes.html
    ├── generate_notes.html
    ├── view_note.html
    ├── images.html
    └── reminders.html
```