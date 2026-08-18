def improve_resume(resume_text):

    suggestions = []

    if "objective" not in resume_text.lower():
        suggestions.append(
            "Add a professional Career Objective section."
        )

    if "project" not in resume_text.lower():
        suggestions.append(
            "Include at least 2 academic or personal projects."
        )

    if "internship" not in resume_text.lower():
        suggestions.append(
            "Add internship or practical experience."
        )

    if "certificate" not in resume_text.lower():
        suggestions.append(
            "Mention certifications like Python, AI, SQL, or Machine Learning."
        )

    if "github" not in resume_text.lower():
        suggestions.append(
            "Add your GitHub profile link."
        )

    if "linkedin" not in resume_text.lower():
        suggestions.append(
            "Add your LinkedIn profile."
        )

    return suggestions