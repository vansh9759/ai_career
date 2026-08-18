def match_resume(skills, job_description):

    # Convert job description to lowercase
    job_description = job_description.lower()

    # Make sure skills is always a list
    if skills is None:
        skills = []

    elif isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]

    matched_skills = []
    missing_skills = []

    required_skills = [
        "python",
        "java",
        "c",
        "c++",
        "html",
        "css",
        "javascript",
        "bootstrap",
        "flask",
        "django",
        "sql",
        "mysql",
        "mongodb",
        "git",
        "github",
        "machine learning",
        "deep learning",
        "tensorflow",
        "keras",
        "numpy",
        "pandas",
        "opencv"
    ]

    # Find matched skills
    for skill in skills:
        if skill.lower() in job_description:
            matched_skills.append(skill.title())

    # Find missing skills
    for skill in required_skills:
        if skill in job_description and skill.title() not in matched_skills:
            missing_skills.append(skill.title())

    total_required = len(matched_skills) + len(missing_skills)

    if total_required == 0:
        score = 0
    else:
        score = int((len(matched_skills) / total_required) * 100)

    return score, matched_skills, missing_skills