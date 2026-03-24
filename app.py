from flask import Flask, render_template, request, redirect, session
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from werkzeug.utils import secure_filename
import nltk
import docx
import os
from PyPDF2 import PdfReader

# Download NLTK
nltk.download("punkt")
nltk.download("stopwords")

app = Flask(__name__)
app.secret_key = "secret123"

# Temporary users
users = {}

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect("/login")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email in users and users[email] == password:
            session["user"] = email
            return redirect("/dashboard")
        else:
            return "Invalid credentials ❌"

    return render_template("login.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if password != confirm:
            return "Passwords do not match ❌"

        users[email] = password
        return redirect("/login")

    return render_template("signup.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")


# ---------------- ANALYZE ----------------
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if "user" not in session:
        return redirect("/login")

    if "resume" not in request.files:
        return render_template("index.html", result="No file uploaded")

    resume = request.files["resume"]
    job_role = request.form.get("job_role")

    if resume.filename == "":
        return render_template("index.html", result="No file selected")

    filename = secure_filename(resume.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    resume.save(file_path)

    text = ""

    if filename.endswith(".docx"):
        doc = docx.Document(file_path)
        text = " ".join([p.text for p in doc.paragraphs]).lower()

    elif filename.endswith(".pdf"):
        reader = PdfReader(file_path)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text().lower()

    else:
        return render_template("index.html", result="Only PDF or DOCX allowed")

    words = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    filtered_words = [w for w in words if w.isalpha() and w not in stop_words]

    job_roles = {
        "data_analyst": ["python", "sql", "excel", "power", "bi", "statistics"],
        "python_developer": ["python", "flask", "django", "api"],
        "web_developer": ["html", "css", "javascript", "react"],
        "java_developer": ["java", "spring"],
        "ai_engineer": ["machine", "learning", "ai", "nlp"]
    }

    required_skills = job_roles.get(job_role, [])

    found_skills = [s for s in required_skills if s in filtered_words]
    missing_skills = list(set(required_skills) - set(found_skills))

    if required_skills and len(found_skills) >= len(required_skills) * 0.6:
        result = "✅ Suitable for selected job role"
    else:
        result = "❌ Not suitable for selected job role"

    return render_template(
        "index.html",
        filename=filename,
        result=result,
        found_skills=found_skills,
        missing_skills=missing_skills
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, port=10000)