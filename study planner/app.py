from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy 
from reportlab.platypus import Image
from datetime import datetime, timedelta
import google.generativeai as genai
import requests
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import atexit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_success.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
genai.configure(api_key=GEMINI_API_KEY)

# Configure Hugging Face API
HF_API_KEY = os.getenv('HF_API_KEY', '')  # Replace with your actual key
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# Email configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = 587
EMAIL_USER = os.getenv('EMAIL_USER', 'aqeel03465568.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '@Aqeel0317')

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# Database Models
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    progress_entries = db.relationship('ProgressEntry', backref='goal', lazy=True)
    reminders = db.relationship('Reminder', backref='goal', lazy=True)

class ProgressEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    entry_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    progress_percentage = db.Column(db.Integer, default=0)

class StudyNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(500))

class GeneratedImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    reminder_date = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(120))
    sent = db.Column(db.Boolean, default=False)
    acknowledged = db.Column(db.Boolean, default=False)

# AI Service Functions
def get_gemini_response(prompt, context=""):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

def generate_study_notes(topic):
    # Generate notes content
    notes_prompt = f"""
    Create comprehensive study notes for the topic: {topic}
    
    Format the notes with:
    1. Clear headings and subheadings
    2. Bullet points for key concepts
    3. Examples where applicable
    4. Summary at the end
    
    Make it suitable for students to study and review.
    """
    content = get_gemini_response(notes_prompt)
    
    # Generate image for the topic
    image_prompt = f"Educational diagram or illustration for {topic}, teaching aid style"
    image_filename = generate_image(image_prompt)
    
    return content, image_filename

def get_coaching_response(message, user_goals, recent_progress):
    context = f"""
    You are a helpful study coach and mentor. The student has the following active goals:
    {user_goals}
    
    Recent progress:
    {recent_progress}
    
    Provide personalized, encouraging, and actionable advice based on their goals and progress.
    """
    return get_gemini_response(message, context)

def generate_image(prompt):
    try:
        payload = {
            "inputs": prompt,
            "options": {
                "wait_for_model": True
            }
        }
        
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload)
        
        if response.status_code == 200:
            # Save image to static folder
            image_filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image_path = os.path.join('static', 'images', image_filename)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            # Save the image
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            # Save to database
            generated_image = GeneratedImage(
                prompt=prompt, 
                image_path=f"images/{image_filename}"  # Store relative path
            )
            db.session.add(generated_image)
            db.session.commit()
            
            return image_filename
        else:
            print(f"Error from Hugging Face API: {response.status_code}")
            print(f"Response content: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

def send_reminder_email(email, title, description):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = email
        msg['Subject'] = f"Study Reminder: {title}"
        
        body = f"""
        Hello!
        
        This is a reminder about your study goal:
        
        {title}
        
        {description}
        
        Keep up the great work!
        
        Best regards,
        Your Student Success Assistant
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

# Add this new function after other AI service functions
def analyze_progress_text(progress_text, goal_description):
    try:
        prompt = f"""
        Based on the following goal description and progress update, estimate the completion percentage (0-100).
        
        Goal: {goal_description}
        Progress Update: {progress_text}
        
        Return only a number between 0 and 100 representing the estimated progress percentage.
        Consider:
        - How much of the goal's requirements are met
        - The quality and depth of the progress
        - Typical milestones for such goals
        """
        
        response = get_gemini_response(prompt)
        # Extract number from response
        percentage = ''.join(filter(str.isdigit, response))
        return min(100, max(0, int(percentage or 0)))
    except Exception as e:
        print(f"Error analyzing progress: {str(e)}")
        return 0

# Routes
@app.route('/')
def index():
    goals = Goal.query.filter_by(completed=False).all()
    recent_progress = ProgressEntry.query.order_by(ProgressEntry.timestamp.desc()).limit(5).all()
    return render_template('index.html', goals=goals, recent_progress=recent_progress)

@app.route('/goals')
def goals():
    goals = Goal.query.all()
    return render_template('goals.html', goals=goals)

@app.route('/add_goal', methods=['GET', 'POST'])
def add_goal():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        target_date = datetime.strptime(request.form['target_date'], '%Y-%m-%d').date()
        
        goal = Goal(title=title, description=description, target_date=target_date)
        db.session.add(goal)
        db.session.commit()
        
        return redirect(url_for('goals'))
    
    return render_template('add_goal.html')

@app.route('/goal/<int:goal_id>')
def view_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    progress_entries = ProgressEntry.query.filter_by(goal_id=goal_id).order_by(ProgressEntry.timestamp.desc()).all()
    return render_template('view_goal.html', goal=goal, progress_entries=progress_entries)

@app.route('/add_progress/<int:goal_id>', methods=['POST'])
def add_progress(goal_id):
    try:
        goal = Goal.query.get_or_404(goal_id)
        entry_text = request.form['entry_text']
        
        # Get AI-generated progress percentage
        progress_percentage = analyze_progress_text(entry_text, goal.description)
        
        progress_entry = ProgressEntry(
            goal_id=goal_id, 
            entry_text=entry_text,
            progress_percentage=progress_percentage
        )
        db.session.add(progress_entry)
        
        # Update goal completion status if progress is 100%
        if progress_percentage == 100:
            goal.completed = True
        
        db.session.commit()
        flash('Progress updated successfully!', 'success')
    except Exception as e:
        print(f"Error adding progress: {str(e)}")
        flash('Error updating progress.', 'error')
    
    return redirect(url_for('view_goal', goal_id=goal_id))

@app.route('/chat')
def chat():
    messages = ChatMessage.query.order_by(ChatMessage.timestamp.desc()).limit(10).all()
    return render_template('chat.html', messages=messages)

@app.route('/chat_message', methods=['POST'])
def chat_message():
    message = request.json['message']
    
    # Get user context
    goals = Goal.query.filter_by(completed=False).all()
    goals_text = "\n".join([f"- {goal.title}: {goal.description}" for goal in goals])
    
    recent_progress = ProgressEntry.query.order_by(ProgressEntry.timestamp.desc()).limit(3).all()
    progress_text = "\n".join([f"- {entry.entry_text}" for entry in recent_progress])
    
    response = get_coaching_response(message, goals_text, progress_text)
    
    # Save to database
    chat_msg = ChatMessage(message=message, response=response)
    db.session.add(chat_msg)
    db.session.commit()
    
    return jsonify({'response': response})

@app.route('/notes')
def notes():
    notes = StudyNote.query.order_by(StudyNote.created_at.desc()).all()
    return render_template('notes.html', notes=notes)

@app.route('/generate_notes', methods=['POST'])
def generate_notes():
    try:
        topic = request.form['topic']
        title = request.form.get('title', f"Notes on {topic}")
        
        content, image_filename = generate_study_notes(topic)
        
        # Create note with image
        note = StudyNote(
            title=title, 
            content=content, 
            topic=topic,
            image_url=image_filename if image_filename else None
        )
        db.session.add(note)
        db.session.commit()
        
        return redirect(url_for('notes'))
    except Exception as e:
        print(f"Error generating notes: {str(e)}")
        flash('Error generating notes. Please try again.', 'error')
        return redirect(url_for('notes')), 500

@app.route('/note/<int:note_id>')
def view_note(note_id):
    note = StudyNote.query.get_or_404(note_id)
    return render_template('view_note.html', note=note)

@app.route('/images')
def images():
    images = GeneratedImage.query.order_by(GeneratedImage.created_at.desc()).all()
    return render_template('images.html', images=images)

@app.route('/generate_image', methods=['POST'])
def generate_image_route():
    try:
        prompt = request.form['prompt']
        if not prompt:
            flash('Please provide a prompt for the image generation.', 'error')
            return redirect(url_for('images'))
            
        image_filename = generate_image(prompt)
        
        if image_filename:
            flash('Image generated successfully!', 'success')
            return redirect(url_for('images'))
        else:
            flash('Failed to generate image. Please try again.', 'error')
            return redirect(url_for('images'))
            
    except Exception as e:
        print(f"Error in generate_image_route: {str(e)}")
        flash('An error occurred while generating the image.', 'error')
        return redirect(url_for('images'))

@app.route('/export_note/<int:note_id>')
def export_note(note_id):
    note = StudyNote.query.get_or_404(note_id)
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    title = Paragraph(note.title, styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Add image if present
    if note.image_url:
        img_path = os.path.join('static', 'images', note.image_url)
        if os.path.exists(img_path):
            story.append(Image(img_path, width=400, height=300))
            story.append(Spacer(1, 12))
    
    # Add content
    content_lines = note.content.split('\n')
    for line in content_lines:
        if line.strip():
            p = Paragraph(line, styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 6))
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{note.title}.pdf",
        mimetype='application/pdf'
    )

@app.route('/reminders')
def reminders():
    reminders = Reminder.query.order_by(Reminder.reminder_date.desc()).all()
    goals = Goal.query.filter_by(completed=False).all()
    return render_template('reminders.html', reminders=reminders, goals=goals)

@app.route('/add_reminder', methods=['POST'])
def add_reminder():
    goal_id = int(request.form['goal_id'])
    title = request.form['title']
    description = request.form.get('description', '')
    reminder_datetime = datetime.strptime(request.form['reminder_datetime'], '%Y-%m-%dT%H:%M')
    email = request.form.get('email', '')
    
    reminder = Reminder(
        goal_id=goal_id,
        title=title,
        description=description,
        reminder_date=reminder_datetime,
        email=email
    )
    db.session.add(reminder)
    db.session.commit()
    
    # Schedule the reminder
    def send_reminder():
        send_reminder_email(email, title, description)
        reminder.sent = True
        db.session.commit()
    
    if reminder_datetime > datetime.now():
        scheduler.add_job(
            func=send_reminder,
            trigger=DateTrigger(run_date=reminder_datetime),
            id=f'reminder_{reminder.id}'
        )
    
    return redirect(url_for('reminders'))

@app.route('/acknowledge_reminder/<int:reminder_id>')
def acknowledge_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    reminder.acknowledged = True
    db.session.commit()
    return redirect(url_for('reminders'))

@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    try:
        note = StudyNote.query.get_or_404(note_id)
        
        # Delete associated image if it exists
        if note.image_url:
            image_path = os.path.join('static', 'images', note.image_url)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting note: {str(e)}")
        flash('Error deleting note.', 'error')
    
    return redirect(url_for('notes'))
# Add this new route after other routes
@app.route('/delete_progress/<int:progress_id>', methods=['POST'])
def delete_progress(progress_id):
    try:
        progress = ProgressEntry.query.get_or_404(progress_id)
        goal_id = progress.goal_id
        
        # Store the goal to check if it's completed
        goal = Goal.query.get(goal_id)
        
        # Delete the progress entry
        db.session.delete(progress)
        
        # Check if the goal should still be marked as completed
        remaining_progress = ProgressEntry.query.filter_by(goal_id=goal_id).all()
        if not any(entry.progress_percentage == 100 for entry in remaining_progress):
            goal.completed = False
        
        db.session.commit()
        flash('Progress entry deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting progress: {str(e)}")
        flash('Error deleting progress entry.', 'error')
    
    return redirect(url_for('view_goal', goal_id=goal_id))

@app.route('/delete_goal/<int:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    try:
        goal = Goal.query.get_or_404(goal_id)
        
        # Delete associated progress entries
        ProgressEntry.query.filter_by(goal_id=goal_id).delete()
        
        # Delete associated reminders
        Reminder.query.filter_by(goal_id=goal_id).delete()
        
        # Delete the goal
        db.session.delete(goal)
        db.session.commit()
        
        flash('Goal and associated data deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting goal: {str(e)}")
        flash('Error deleting goal.', 'error')
    
    return redirect(url_for('goals'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)