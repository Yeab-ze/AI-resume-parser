import os
import uuid
from flask import Flask, request, render_template
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename
from resumeparser import ats_extractor

UPLOAD_PATH = "__DATA__"
os.makedirs(UPLOAD_PATH, exist_ok=True)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/process", methods=["POST"])
def ats():
    # Check file exists
    if 'pdf_doc' not in request.files:
        return render_template('index.html', error="No file uploaded")

    doc = request.files.get('pdf_doc')

    if doc.filename == "":
        return render_template('index.html', error="No file selected")

    # Optional job description
    jd = request.form.get('job_description')

    # Safe filename
    filename = f"{uuid.uuid4()}_{secure_filename(doc.filename)}"
    doc_path = os.path.join(UPLOAD_PATH, filename)
    doc.save(doc_path)

    try:
        resume_text = _read_file_from_path(doc_path)

        if not resume_text.strip():
            return render_template('index.html', error="Could not extract text from PDF")

        parsed_data = ats_extractor(resume_text, jd)
        
        if isinstance(parsed_data, dict) and "error" in parsed_data:
            return render_template('index.html', error=parsed_data["error"])

    except Exception as e:
        return render_template('index.html', error=f"Processing error: {str(e)}")

    finally:
        # Clean up file
        if os.path.exists(doc_path):
            os.remove(doc_path)

    return render_template('index.html', data=parsed_data)


def _read_file_from_path(path):
    data = ""
    try:
        with fitz.open(path) as doc:
            for page in doc:
                text = page.get_text()
                if text:
                    data += text + "\n"
    except Exception as e:
        print(f"Error reading PDF with PyMuPDF: {e}")
        
    return data


if __name__ == "__main__":
    app.run(port=8000, debug=True)