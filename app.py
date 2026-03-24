from flask import Flask, render_template, request, redirect, url_for, session
import os
import PyPDF2
import docx

app = Flask(__name__)
app.secret_key = "secret123"

# Temporary user storage (resets on restart)
users = {}

# ---------------- HOME ----------------
@app.route('/')
def home():
    if 'user' in session:
        return render_template("index.html")
    return redirect(url_for('login'))

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users:
            return "User already exists ❌"

        users[email] = password
        return redirect(url_for('login'))

    return render_template("signup.html")

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users and users[email] == password:
            session['user'] = email
            return redirect(url_for('home'))
        else:
            return "Invalid credentials ❌"

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ---------------- ANALYZE ----------------
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'user' not in session:
            return redirect(url_for('login'))

        file = request.files['resume']
        job_role = request.form.get('job_role')

        if file.filename == '':
            return "No file selected ❌"

        text = ""

        # PDF
        if file.filename.endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""

        # DOCX
        elif file.filename.endswith('.docx'):
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text

        else:
            return "Unsupported file ❌"

        text = text.lower()

        skills = ["python", "java", "sql", "machine learning", "html", "css", "flask"]

        found_skills = [s for s in skills if s in text]
        missing_skills = [s for s in skills if s not in text]

        result = f"Role: {job_role} | Found {len(found_skills)} skills"

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