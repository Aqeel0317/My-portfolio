import os
import io
import fitz  # PyMuPDF library
import google.generativeai as genai
# Removed: import requests
import pytesseract # Import pytesseract
from flask import Flask, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv
from PIL import Image # Keep for image validation/opening non-PDFs and pytesseract
from datetime import datetime

# --- Configuration ---
load_dotenv()

# Flask App Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key_change_me')

# Gemini API Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY environment variable.")
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    raise RuntimeError(f"Failed to configure or initialize Gemini API: {e}")

# --- Tesseract Configuration (Optional but Recommended) ---
# If Tesseract is not in your system's PATH, uncomment and set the path below
# Replace with your actual Tesseract installation path
# Example for Windows:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Example for Linux (if installed in a non-standard location):
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'


# REMOVED: Hugging Face API Configuration

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Helper Function for OCR (Using Tesseract) ---
def get_text_from_image_bytes(image_bytes):
    """Performs OCR using Tesseract on image bytes and returns extracted text."""
    try:
        # Convert image bytes to a PIL Image object
        img = Image.open(io.BytesIO(image_bytes))

        # Perform OCR using pytesseract
        # Specify language(s) - e.g., 'eng' for English. Use '+' for multiple, e.g., 'eng+fra'
        text = pytesseract.image_to_string(img, lang='eng')

        app.logger.info(f"Tesseract OCR successful, extracted ~{len(text)} chars.")
        return text.strip() # Return stripped text

    except pytesseract.TesseractNotFoundError:
        error_msg = "[Tesseract OCR Error: Executable not found. Check installation and PATH/configuration]"
        app.logger.error(error_msg)
        return error_msg
    except Exception as e:
        # Catch other potential errors (e.g., PIL errors, Tesseract processing errors)
        error_msg = f"[Tesseract OCR Error: {type(e).__name__} - {e}]"
        app.logger.error(error_msg, exc_info=True)
        return error_msg

# --- Routes ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main welcome page."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template('index.html', current_time=now)

@app.route('/upload', methods=['GET'])
def upload_page():
    """Renders the file upload page."""
    return render_template('upload.html', allowed_extensions=ALLOWED_EXTENSIONS)


@app.route('/process', methods=['POST'])
def process_image():
    """Handles file upload (Image or PDF), extracts text, and processes via Gemini."""
    if 'file' not in request.files:
        flash('No file part selected.', 'danger')
        return redirect(url_for('upload_page'))

    file = request.files['file']
    question = request.form.get('question', '').strip()

    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('upload_page'))

    if not allowed_file(file.filename):
        flash(f'Invalid file type. Allowed types are: {", ".join(sorted(list(ALLOWED_EXTENSIONS)))}', 'warning')
        return redirect(url_for('upload_page'))

    filename = file.filename
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    extracted_text = ""

    try:
        file_bytes = file.read()

        # --- Text Extraction Logic ---
        if file_extension == 'pdf':
            app.logger.info(f"Processing PDF file: {filename}")
            all_pages_text = []
            pdf_doc = None
            try:
                pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            except Exception as pdf_err:
                flash(f"Error opening PDF: {pdf_err}. It might be corrupted, password-protected, or an invalid PDF.", 'danger')
                return redirect(url_for('upload_page'))

            num_pages = len(pdf_doc)
            app.logger.info(f"PDF has {num_pages} pages.")

            for page_num in range(num_pages):
                page_text = ""
                try:
                    page = pdf_doc.load_page(page_num)
                    # Try direct text extraction first
                    page_text = page.get_text("text").strip()

                    # Use Tesseract OCR if direct extraction yields little text
                    if len(page_text) < 50: # Keep threshold or adjust
                        app.logger.info(f"Page {page_num + 1}: Minimal text found via direct extraction, attempting Tesseract OCR.")
                        zoom = 300 / 72 # Render at 300 DPI
                        mat = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=mat, alpha=False)

                        if pix.width == 0 or pix.height == 0:
                            app.logger.warning(f"Page {page_num + 1}: Skipping empty page rendering.")
                            continue

                        # Get image bytes for the page
                        img_bytes_page = pix.tobytes("png")
                        if img_bytes_page:
                            # Call Tesseract OCR helper
                            ocr_text = get_text_from_image_bytes(img_bytes_page)
                            # Check if OCR was successful before replacing direct text
                            if not ocr_text.startswith("[Tesseract OCR Error:"):
                                # If direct text was minimal AND OCR found something, use OCR text.
                                # If both were minimal/empty, keep the (likely empty) ocr_text.
                                page_text = ocr_text
                                app.logger.info(f"Page {page_num + 1}: Tesseract OCR extracted ~{len(page_text)} chars.")
                            else:
                                app.logger.warning(f"Page {page_num + 1}: Tesseract OCR failed or returned error: {ocr_text}. Keeping direct text (if any).")
                                # Flash message could be added here too
                                # flash(f"OCR failed for page {page_num+1}: {ocr_text}", "warning")
                        else:
                            app.logger.warning(f"Page {page_num + 1}: Failed to get image bytes for Tesseract OCR.")
                    else:
                         app.logger.info(f"Page {page_num + 1}: Direct text extraction got ~{len(page_text)} chars.")

                except Exception as page_err:
                    app.logger.error(f"Error processing PDF page {page_num + 1}: {page_err}", exc_info=True)
                    page_text = f"\n[Error processing page {page_num + 1}]\n"

                all_pages_text.append(f"\n--- Page {page_num + 1} ---\n{page_text}") # Use stripped page_text

            if pdf_doc:
                pdf_doc.close()
            extracted_text = "".join(all_pages_text)

        elif file_extension in ALLOWED_EXTENSIONS: # Image file processing
             app.logger.info(f"Processing Image file: {filename}")
             # Call Tesseract OCR helper directly
             extracted_text = get_text_from_image_bytes(file_bytes)

        else: # Fallback
            flash(f"Unsupported file type: {file_extension}", "danger")
            return redirect(url_for('upload_page'))


        # --- Post-Extraction Check (Updated for Tesseract errors) ---
        # Check if text is empty OR if it contains the Tesseract error marker
        is_error_text = extracted_text.startswith("[Tesseract OCR Error:")
        if not extracted_text or extracted_text.strip() == "" or is_error_text:
             if is_error_text:
                 # Display the specific Tesseract error if available
                 flash(f"Text extraction failed. Reason: {extracted_text}", 'warning')
             else:
                 flash("Could not extract meaningful text from the file. It might be empty or purely graphical.", 'warning')
             return redirect(url_for('upload_page'))

        app.logger.info(f"Total extracted text length: {len(extracted_text)} characters.")

        # --- Call Gemini API (No changes needed here) ---
        # ... (rest of the Gemini call and result rendering remains the same) ...
        prompt_context = f"""You are an AI assistant specialized in analyzing and summarizing documents.
Based *only* on the following text extracted from a document named '{filename}', perform the requested task.
If the information needed to answer a question is not present in the text, clearly state that.
Do not add any information not found in the text. Format your response clearly."""

        if question:
            prompt = f"""{prompt_context}

User's Question: {question}

Extracted Text:
--- START TEXT ---
{extracted_text}
--- END TEXT ---

Answer based *only* on the text above:"""
            task_description = f"Answer for question: \"{question}\" from document: {filename}"
        else:
            prompt = f"""{prompt_context}

Task: Please summarize the following text extracted from the document.
Provide a concise main summary followed by key points listed as bullet points.

Extracted Text:
--- START TEXT ---
{extracted_text}
--- END TEXT ---

Summary and Key Points based *only* on the text above:"""
            task_description = f"Summary of the document: {filename}"

        try:
            gemini_response = gemini_model.generate_content(prompt)

            # More robust check for blocked content or empty response
            if not gemini_response.candidates or not gemini_response.candidates[0].content.parts:
                finish_reason = gemini_response.candidates[0].finish_reason if gemini_response.candidates else "Unknown"
                safety_ratings = gemini_response.candidates[0].safety_ratings if gemini_response.candidates else "N/A"
                app.logger.error(f"Gemini response issue. Finish Reason: {finish_reason}, Safety Ratings: {safety_ratings}")

                if finish_reason == 'SAFETY':
                     answer = "The response was blocked by the Gemini API due to safety filters..." # Shortened for brevity
                     flash("Response blocked by safety filters.", "warning")
                elif finish_reason == 'RECITATION':
                     answer = "The response was blocked because it may contain material from protected sources..." # Shortened
                     flash("Response blocked due to potential recitation.", "warning")
                else:
                     answer = f"Gemini API returned an empty or incomplete response. Finish Reason: {finish_reason}"
                     flash("Received an empty or incomplete response from the AI.", "warning")
                # Still render result page but with the error message
                return render_template('result.html',
                                    task_description=task_description,
                                    answer=answer,
                                    extracted_text="[Not displaying extracted text due to response error]",
                                    user_question=question)
            else:
                answer = gemini_response.text


            # --- Display Result ---
            return render_template('result.html',
                                   task_description=task_description,
                                   answer=answer,
                                   extracted_text=extracted_text, # Pass combined text
                                   user_question=question)

        except Exception as e:
            # Catch potential errors during Gemini generation (e.g., API errors, quota issues)
            app.logger.error(f"Error during Gemini API call: {e}", exc_info=True)
            flash(f"An error occurred while communicating with the AI model: {type(e).__name__}. Please try again later.", 'danger')
            return redirect(url_for('upload_page'))


    # --- Global Error Handling for file processing issues ---
    except genai.types.generation_types.BlockedPromptException as e:
         # This might be caught above, but good as a fallback
        app.logger.error(f"Gemini Prompt Blocked: {e}", exc_info=True)
        flash(f"The request was blocked by the Gemini API before generation, likely due to safety filters on the prompt/extracted text: {e}", 'danger')
        return redirect(url_for('upload_page'))
    except Exception as e:
        app.logger.error(f"An error occurred during processing file {filename}: {e}", exc_info=True)
        flash(f"An unexpected error occurred during file processing: {type(e).__name__}. Check server logs.", 'danger')
         # Redirect to the upload page
        return redirect(url_for('upload_page'))


# --- Run the App ---
if __name__ == '__main__':
    # REMOVED: Hugging Face Token Check
    # REMOVED: Google Application Credentials Check

    # Optional: Add a check/warning if Tesseract path isn't explicitly set and might not be found
    try:
        pytesseract.get_tesseract_version()
        print(f"Tesseract found successfully: Version {pytesseract.get_tesseract_version()}")
    except pytesseract.TesseractNotFoundError:
        print("WARNING: Tesseract executable not found in PATH.")
        print("Ensure Tesseract OCR engine is installed and its path is configured in app.py if needed.")

    print(f"Flask Secret Key: {app.config['SECRET_KEY']}")
    app.run(debug=True, host='0.0.0.0', port=5000)