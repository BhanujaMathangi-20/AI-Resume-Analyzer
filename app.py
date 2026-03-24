from flask import Flask, render_template, request, redirect, url_for
import os
import PyPDF2
import docx

app = Flask(__name__)

# ---------------- USERS STORAGE ----------------
users = {}

# ---------------- HOME ----------------
@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users[email] = password
        return redirect(url_for('login'))

    return render_template('signup.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users and users[email] == password:
            return redirect(url_for('index'))
        else:
            return "Invalid credentials ❌"

    return render_template('login.html')

# ---------------- INDEX ----------------
@app.route('/index')
def index():
    return render_template('index.html')

# ---------------- RESUME ANALYZER ----------------
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files['resume']

        if file.filename == '':
            return "No file selected ❌"

        text = ""

        # -------- PDF --------
        if file.filename.endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""

        # -------- DOCX --------
        elif file.filename.endswith('.docx'):
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text

        else:
            return "Unsupported file format ❌"

        text = text.lower()

        skills = ["python", "java", "sql", "machine learning", "html", "css", "flask"]
        found_skills = [s for s in skills if s in text]
        missing_skills = [s for s in skills if s not in text]

        result = f"Found {len(found_skills)} skills"

        return render_template(
            "index.html",
            result=result,
            found_skills=found_skills,
            missing_skills=missing_skills
        )

    except Exception as e:
        return f"Error occurred: {str(e)}"

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)