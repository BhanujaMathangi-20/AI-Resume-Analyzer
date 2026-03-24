from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)
app.secret_key = "secret123"

# -------- Upload Folder --------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------- Database Setup --------
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT, password TEXT)')
    conn.commit()
    conn.close()

init_db()

# -------- Home --------
@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

# -------- Login --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = email
            return redirect(url_for('home'))
        else:
            error = "Invalid email or password"

    return render_template('login.html', error=error)

# -------- Signup --------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('signup.html')

# -------- Logout --------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# -------- Analyze Resume --------
@app.route('/analyze', methods=['POST'])
def analyze():
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
                if page.extract_text():
                    text += page.extract_text()

        # DOCX
        elif file.filename.endswith('.docx'):
            doc = Document(filepath)
            for para in doc.paragraphs:
                text += para.text

        text = text.lower()

        skills_db = {
            "python developer": ["python", "flask", "sql", "html", "css"],
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

# -------- Run --------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)