# Resume Parser — AI Powered ATS Checker

A Flask web application that parses resumes in PDF format using AI (via OpenRouter or Google Gemini) and provides detailed ATS compatibility analysis.

## ✨ Features

- **PDF Upload & Text Extraction** — Automatically extracts text from PDF resumes
- **AI-Powered Parsing** — Uses Meta Llama 3.1 70B or Google Gemini 1.5 Flash
- **ATS Score** — Rates resume compatibility on a 0-100 scale
- **Structured Data Extraction**:
  - Full name, email, phone, LinkedIn, GitHub
  - Employment history (company, role, duration)
  - Education (institution, degree, field)
  - Technical and soft skills
- **Job Description Matching** — Optional JD analysis for:
  - Missing keywords
  - Targeted improvement suggestions
  - Skill gap analysis
- **Beautiful UI** — Modern, responsive web interface
- **Security Focused** — API keys never logged or exposed

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10+ |
| Framework | Flask 3.0+ |
| PDF Processing | PyMuPDF (fitz) |
| AI API | OpenAI SDK (OpenRouter/Gemini) |
| Frontend | HTML5, CSS3, Vanilla JS |
| Configuration | PyYAML |

---

## 📁 Project Structure

```
resume-parser/
├── app.py                    # Flask app & routes
├── resumeparser.py           # AI extraction logic
├── config.yaml              # API configuration (add to .gitignore)
├── .env                     # Environment variables (add to .gitignore)
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
├── templates/
│   └── index.html          # Frontend UI
├── uploads/                # Temporary upload folder (auto-created)
└── README.md               # This file
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/resume-parser.git
cd resume-parser
```

### 2. Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

**Option A: Environment Variable (Recommended)**

```bash
# macOS/Linux
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Windows
set OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Option B: Using .env file**

Copy `.env` to `.env.local` (never commit):

```bash
cp .env .env.local
```

Edit `.env.local`:

```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Option C: Using config.yaml**

⚠️ **NOT RECOMMENDED** — but if you must:

```yaml
# config.yaml
OPENROUTER_API_KEY: "sk-or-v1-your-key-here"
```

Then **immediately** add to `.gitignore`:

```bash
echo "config.yaml" >> .gitignore
```

### 5. Get an API Key

- **OpenRouter** (Recommended): https://openrouter.ai/keys
  - Free credits for testing
  - Multiple model options
  - Pay-as-you-go pricing

- **Google Gemini**: https://makersuite.google.com/app/apikey
  - Free tier available
  - Automatic API key detection

### 6. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:8000`

---

## 📖 Usage

1. Open `http://localhost:8000` in your browser
2. **Upload** your resume as a PDF (max 5MB)
3. **Optionally paste** a job description for targeted analysis
4. Click **"Analyse Resume"** and wait for results
5. Review your **ATS score**, **missing keywords**, and **improvement suggestions**

---

## 📊 Output Fields

| Field | Description | Type |
|-------|-------------|------|
| `full_name` | Candidate's full name | string |
| `email` | Email address | string |
| `phone` | Phone number | string |
| `linkedin` | LinkedIn profile URL | string |
| `github` | GitHub profile URL | string |
| `employment_details` | List of job positions | array |
| `education` | List of degrees/institutions | array |
| `technical_skills` | Programming, tools, frameworks, etc. | array |
| `soft_skills` | Communication, leadership, teamwork, etc. | array |
| `resume_score` | ATS compatibility score (0-100) | integer |
| `pass_fail` | Pass (≥70) or Fail (<70) | string |
| `missing_keywords` | Keywords from JD not found in resume | array |
| `suggestions` | Specific improvement recommendations | array |

---

## 🔒 Security Best Practices

### ✅ DO

- ✅ Use **environment variables** for API keys
- ✅ Add `config.yaml` and `.env` to `.gitignore`
- ✅ Rotate API keys if accidentally exposed
- ✅ Use HTTPS in production
- ✅ Limit file upload size (already set to 5MB)
- ✅ Validate file types (only PDF accepted)

### ❌ DON'T

- ❌ Commit API keys to version control
- ❌ Hardcode secrets in source code
- ❌ Share API keys in emails or chats
- ❌ Use production keys in development
- ❌ Remove sensitive files from `.gitignore`

---

## 🚨 If Your API Key Is Exposed

1. **Immediately rotate** the key at your provider's dashboard
2. **Never commit** the exposed key again
3. **Update** your environment variables with the new key
4. **Review** your account for suspicious activity

---

## 📝 Example curl Request

```bash
curl -X POST http://localhost:8000/process \
  -F "pdf_doc=@resume.pdf" \
  -F "job_description=Python developer with 5+ years experience"
```

---

## 🛠️ Troubleshooting

### API Key Not Found

```
Error: API key not found
```

**Solution:** Ensure `OPENROUTER_API_KEY` or `OPENAI_API_KEY` is set:

```bash
# Check if set
echo $OPENROUTER_API_KEY

# Or set it
export OPENROUTER_API_KEY="your-key-here"
```

### "Could not extract text from PDF"

- The PDF may be scanned/image-based
- Try an OCR-processed version
- Ensure PDF is valid and not corrupted

### Rate Limiting (429 Error)

- Wait before retrying (app auto-retries 3x)
- Check your API quotas
- Upgrade your plan if needed

### File Too Large

```
Error: File is too large
```

Max file size is 5MB. Check your PDF size:

```bash
ls -lh resume.pdf
```

### Port Already in Use

```
OSError: [Errno 48] Address already in use
```

Change the port in `app.py`:

```python
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)
```

---

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

```bash
docker build -t resume-parser .
docker run -p 8000:8000 -e OPENROUTER_API_KEY="your-key" resume-parser
```

---

## 📄 License

MIT License — free to use and modify

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## ❓ FAQ

**Q: Can I use this with other LLMs?**  
A: Yes! The code uses the OpenAI SDK which works with OpenRouter, Google Gemini, and other compatible APIs.

**Q: Is my resume data stored?**  
A: No. Files are uploaded, processed, and immediately deleted. No data is stored server-side.

**Q: What happens if the PDF is corrupted?**  
A: The app will return an error. Ensure your PDF is valid and readable.

**Q: Can I run this locally without internet?**  
A: No, you need internet to call the AI API. The frontend works offline, but parsing requires an API.

---

## 📧 Support

For issues or questions:
- Open an GitHub Issue
- Check the troubleshooting section above
- Review API provider documentation

---

**Made with ❤️ for job seekers**
