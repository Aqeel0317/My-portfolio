import os
import uuid
import base64
# NO BytesIO
from flask import (
    Flask, render_template, request, redirect, url_for, session,
    # NO make_response needed for this version beyond default error handling
    abort
)
from werkzeug.utils import secure_filename
# NO xhtml2pdf

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_key_for_html_print_hybrid') # Changed default

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_file_as_base64_data(filepath):
    """Reads an image file and returns its base64 encoded data URI."""
    if not filepath or not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        mime_type = f"image/{filepath.rsplit('.', 1)[1].lower()}"
        if mime_type == "image/jpg": mime_type = "image/jpeg"
        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"Error encoding image {filepath}: {e}")
        return None

# NO html_to_pdf function needed

# --- Routes ---
@app.route('/')
def index():
    """Displays the main CV input form."""
    session.pop('cv_data', None)
    session.pop('image_path', None)
    # Make sure index.html includes 'professional_title' input field
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_form():
    """Processes form data, saves image, stores in session."""
    if request.method == 'POST':
        cv_data = {}
        # --- Basic Info (including professional_title) ---
        cv_data['name'] = request.form.get('name', 'N/A')
        cv_data['email'] = request.form.get('email', 'N/A')
        cv_data['phone'] = request.form.get('phone', 'N/A')
        cv_data['linkedin'] = request.form.get('linkedin', '')
        cv_data['portfolio'] = request.form.get('portfolio', '')
        cv_data['address'] = request.form.get('address', 'N/A')
        cv_data['summary'] = request.form.get('summary', '')
        cv_data['professional_title'] = request.form.get('professional_title', '') # Get optional title

        # --- Dynamic Skills ---
        cv_data['skills'] = [
            request.form[key] for key in request.form
            if key.startswith('skill_') and request.form[key].strip()
        ]
        # --- Dynamic Experience ---
        cv_data['experience'] = []
        exp_indices = sorted(list(set([key.split('_')[-1] for key in request.form if key.startswith('job_title_')])))
        for index in exp_indices:
            title = request.form.get(f'job_title_{index}')
            company = request.form.get(f'company_{index}')
            years = request.form.get(f'exp_years_{index}')
            desc = request.form.get(f'exp_desc_{index}')
            if title and company:
                cv_data['experience'].append({'title': title, 'company': company, 'years': years, 'description': desc})
        # --- Dynamic Education ---
        cv_data['education'] = []
        edu_indices = sorted(list(set([key.split('_')[-1] for key in request.form if key.startswith('degree_')])))
        for index in edu_indices:
            degree = request.form.get(f'degree_{index}')
            institution = request.form.get(f'institution_{index}')
            edu_years = request.form.get(f'edu_years_{index}')
            if degree and institution:
                 cv_data['education'].append({'degree': degree, 'institution': institution, 'years': edu_years})

        # --- Profile Picture Handling ---
        image_path = None
        if 'picture' in request.files:
            file = request.files['picture']
            if file and file.filename != '' and allowed_file(file.filename):
                try:
                    filename = secure_filename(file.filename)
                    ext = filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4()}.{ext}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
                    image_path = filepath
                except Exception as e:
                    print(f"Error saving file: {e}")
                    pass # Continue without image

        # Store data and image path in session
        session['cv_data'] = cv_data
        session['image_path'] = image_path
        return redirect(url_for('select_template'))
    return redirect(url_for('index'))

@app.route('/select_template')
def select_template():
    """Displays template choices."""
    if 'cv_data' not in session:
        return redirect(url_for('index'))

    # List all available templates
    available_templates = [
         {'id': 1, 'name': 'Classic Minimalist', 'thumbnail': url_for('static', filename='images/template1_thumb.png')},
         {'id': 4, 'name': 'Modern Two-Column', 'thumbnail': url_for('static', filename='images/template4_thumb.png')},
       
         {'id': 2, 'name': 'Modern Side Bar', 'thumbnail': url_for('static', filename='images/template2_thumb.png')},
         {'id': 3, 'name': 'Creative Two Column', 'thumbnail': url_for('static', filename='images/template3_thumb.png')},
         {'id': 5, 'name': 'Elegant Timeline', 'thumbnail': url_for('static', filename='images/template5_thumb.png')}, # Add template5_thumb.png
        {'id': 6, 'name': 'Bold Header', 'thumbnail': url_for('static', filename='images/template6_thumb.png')},        # Add template6_thumb.png
    ]
    
    return render_template('select_template.html', templates=available_templates)


@app.route('/generate/<int:template_id>')
def generate_cv(template_id):
    """Renders the CV as an HTML page using the selected template and session data."""
    if 'cv_data' not in session:
        return redirect(url_for('index'))

    cv_data = session['cv_data']
    image_path = session.get('image_path') # Get path from session

    # Get Base64 encoded image data (still useful for self-contained HTML/print)
    cv_data['profile_pic_base64'] = get_image_file_as_base64_data(image_path)

    # --- Select Template ---
    template_name = f'cv_template_{template_id}.html'
    template_full_path = os.path.join(app.template_folder, template_name)

    if not os.path.exists(template_full_path):
        print(f"Error: Template file not found at {template_full_path}")
        abort(404, description=f"Selected CV template ({template_name}) not found.")

    # --- Render HTML Page Directly ---
    try:
        # Directly render the template. Flask handles the HTML response.
        return render_template(template_name, user_data=cv_data)
    except Exception as e:
        print(f"Error rendering template {template_name}: {e}")
        abort(500, description="Error rendering CV template.")

# --- Error Handling ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', error=e), 500

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)