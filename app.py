import os
import uuid
import logging
from flask import Flask, request, render_template, jsonify
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename
from resumeparser import ats_extractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_PATH = "uploads"
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_PATH, exist_ok=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _read_file_from_path(path):
    """Extract text from PDF file."""
    data = ""
    try:
        with fitz.open(path) as doc:
            for page in doc:
                text = page.get_text()
                if text:
                    data += text + "\n"
    except Exception as e:
        logger.error(f"Error reading PDF with PyMuPDF: {e}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    return data


@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route("/process", methods=["POST"])
def process_resume():
    """Process uploaded resume and extract ATS information."""
    
    # Validate file exists
    if 'pdf_doc' not in request.files:
        return render_template('index.html', error="No file uploaded"), 400

    file = request.files.get('pdf_doc')

    if file.filename == "":
        return render_template('index.html', error="No file selected"), 400

    # Validate file type
    if not allowed_file(file.filename):
        return render_template('index.html', error="Only PDF files are allowed"), 400

    # Optional job description
    job_description = request.form.get('job_description', '').strip()

    # Save file with secure name
    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(UPLOAD_PATH, filename)
    
    try:
        file.save(file_path)
        logger.info(f"File saved: {filename}")

        # Extract text from PDF
        resume_text = _read_file_from_path(file_path)

        if not resume_text.strip():
            return render_template('index.html', error="Could not extract text from PDF"), 400

        # Parse resume with AI
        logger.info("Parsing resume with AI...")
        parsed_data = ats_extractor(resume_text, job_description if job_description else None)
        
        # Check for errors
        if isinstance(parsed_data, dict) and "error" in parsed_data:
            logger.error(f"AI parsing error: {parsed_data['error']}")
            return render_template('index.html', error=parsed_data["error"]), 400

        logger.info("Resume parsed successfully")
        return render_template('index.html', data=parsed_data), 200

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return render_template('index.html', error=str(ve)), 400

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return render_template('index.html', error=f"Processing error: {str(e)}"), 500

    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up file: {filename}")
            except Exception as e:
                logger.warning(f"Could not delete file {filename}: {e}")


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return render_template('index.html', error="File is too large. Maximum size is 5MB"), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server error."""
    logger.error(f"Internal server error: {error}")
    return render_template('index.html', error="Internal server error. Please try again."), 500


def handler(request):
    return app(request.environ, request.start_response)
