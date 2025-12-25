@app.route('/analyze', methods=['POST'])
def analyze_resume():

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

    # Read resume text (ONLY DOCX supported)
    if not filename.lower().endswith(".docx"):
        return render_template(
            "index.html",
            result="❌ Please upload a DOCX file only"
        )

    doc = docx.Document(file_path)
    text = " ".join([para.text for para in doc.paragraphs]).lower()

    # NLP processing
    words = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_words = [w for w in words if w.isalpha() and w not in stop_words]

    job_roles = {
        "data_analyst": ["python", "sql", "excel", "power", "bi", "data", "analysis", "statistics"],
        "python_developer": ["python", "flask", "django", "api", "oop", "sql"],
        "web_developer": ["html", "css", "javascript", "react", "bootstrap"]
    }

    required_skills = job_roles.get(job_role, [])
    found_skills = sorted(skill for skill in required_skills if skill in filtered_words)
    missing_skills = sorted(set(required_skills) - set(found_skills))

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
