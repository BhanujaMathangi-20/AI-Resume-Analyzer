from flask import Flask, render_template, request
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from werkzeug.utils import secure_filename
import docx
import os

app = Flask(__name__)

# Folder to save uploaded resumes
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Analyze resume
@app.route('/analyze', methods=['POST'])
def analyze_resume():

    # Check resume file
    if 'resume' not in request.files:
        return render_template('index.html', result="No file uploaded")

    resume = request.files['resume']
    job_role = request.form.get('job_role')

    if resume.filename == '':
        return render_template('index.html', result="No file selected")

    # Save resume
    filename = secure_filename(resume.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    resume.save(file_path)

    # Read resume text (DOCX)
    doc = docx.Document(file_path)
    text = " ".join([para.text for para in doc.paragraphs]).lower()

    # NLP processing
    words = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_words = [w for w in words if w.isalpha() and w not in stop_words]

    # Job role skill requirements
    job_roles = {
        "data_analyst": [
            "python", "sql", "excel", "power", "bi",
            "data", "analysis", "statistics"
        ],
        "python_developer": [
            "python", "flask", "django", "api",
            "oop", "sql"
        ],
        "web_developer": [
            "html", "css", "javascript",
            "react", "bootstrap"
        ]
    }

    required_skills = job_roles.get(job_role, [])

    found_skills = sorted(set(skill for skill in required_skills if skill in filtered_words))
    missing_skills = sorted(set(required_skills) - set(found_skills))

    # Suitability logic
    if required_skills and len(found_skills) >= len(required_skills) * 0.6:
        result = "✅ Suitable for selected job role"
    else:
        result = "❌ Not suitable for selected job role"

    return render_template(
        'index.html',
        filename=filename,
        result=result,
        found_skills=found_skills,
        missing_skills=missing_skills
    )

if __name__ == '__main__':
    app.run(debug=True)
