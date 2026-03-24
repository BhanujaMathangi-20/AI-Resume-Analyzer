from flask import Flask, render_template, request, redirect, url_for, session
import os
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------- HOME ----------------
@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == "test@gmail.com" and password == "123":
            session['user'] = email
            return redirect(url_for('home'))
        else:
            error = "Invalid email or password"

    return render_template('login.html', error=error)


# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template('signup.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# ---------------- ANALYZE ----------------
@app.route('/analyze', methods=['POST'])
def analyze():

    # 🔐 protect route
    if 'user' not in session:
        return redirect(url_for('login'))

    job_role = request.form['job_role']
    file = request.files['resume']

    if file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        text = ""

        # PDF
        if file.filename.endswith('.pdf'):
            reader = PdfReader(filepath)
            for page in reader.pages:
                text += page.extract_text()

        # DOCX
        elif file.filename.endswith('.docx'):
            doc = Document(filepath)
            for para in doc.paragraphs:
                text += para.text

        text = text.lower()

        skills_db = {
            "python developer": ["python", "flask", "sql", "html", "css"],
            "data analyst": ["python", "sql", "excel", "pandas"],
            "web developer": ["html", "css", "javascript"],
            "java developer": ["java", "spring"],
            "ai engineer": ["python", "machine learning"]
        }

        required_skills = skills_db.get(job_role, [])

        found_skills = [skill for skill in required_skills if skill in text]
        missing_skills = [skill for skill in required_skills if skill not in text]

        result = f"Role: {job_role} | Found {len(found_skills)} skills"

        return render_template(
            'index.html',
            result=result,
            found_skills=found_skills,
            missing_skills=missing_skills
        )

    return "No file uploaded"


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)