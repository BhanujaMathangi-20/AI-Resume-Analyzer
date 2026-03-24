from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import docx
import PyPDF2
import os

# Download NLTK data
nltk.download("punkt")
nltk.download("stopwords")

app = Flask(__name__)
app.secret_key = "secret123"

# Temporary user storage
users = {}

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email in users and users[email] == password:
            session["user"] = email
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if password != confirm:
            return render_template("signup.html", error="Passwords do not match")

        if email in users:
            return render_template("signup.html", error="User already exists")

        users[email] = password
        return redirect(url_for("login"))

    return render_template("signup.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("index.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- ANALYZE ----------------
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if "user" not in session:
        return redirect(url_for("login"))

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

    # -------- DOCX --------
    if filename.lower().endswith(".docx"):
        try:
            doc = docx.Document(file_path)
            text = " ".join([para.text for para in doc.paragraphs])
        except:
            return render_template("index.html", result="Error reading DOCX")

    # -------- PDF --------
    elif filename.lower().endswith(".pdf"):
        try:
            pdf = PyPDF2.PdfReader(file_path)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        except:
            return render_template("index.html", result="Error reading PDF")

    else:
        return render_template("index.html", result="Upload PDF or DOCX only")

    # -------- SAFETY CHECK --------
    if not text.strip():
        return render_template("index.html", result="Could not read file content")

    text = text.lower()

    # -------- NLP --------
    words = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    filtered_words = [w for w in words if w.isalpha() and w not in stop_words]

    # -------- JOB ROLES --------
    job_roles = {
        "data_analyst": ["python", "sql", "excel", "powerbi", "data", "analysis"],
        "python_developer": ["python", "flask", "django", "api"],
        "web_developer": ["html", "css", "javascript", "react", "bootstrap"],
        "java_developer": ["java", "spring", "hibernate"],
        "ai_engineer": ["python", "machine", "learning", "ai"]
    }

    required_skills = job_roles.get(job_role, [])

    found_skills = [skill for skill in required_skills if skill in filtered_words]
    missing_skills = list(set(required_skills) - set(found_skills))

    if required_skills and len(found_skills) >= len(required_skills) * 0.6:
        result = "✅ Suitable for selected job role"
    else:
        result = "❌ Not suitable for selected job role"

    return render_template(
        "index.html",
        result=result,
        found_skills=found_skills,
        missing_skills=missing_skills
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)