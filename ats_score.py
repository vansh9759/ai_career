def calculate_ats_score(text):

    score = 0
    suggestions = []

    text = text.lower()

    # Email
    if "@" in text:
        score += 10
    else:
        suggestions.append("Add an email address.")

    # Phone
    if any(ch.isdigit() for ch in text):
        score += 10
    else:
        suggestions.append("Add a phone number.")

    # Education
    if "b.tech" in text or "btech" in text or "education" in text:
        score += 15
    else:
        suggestions.append("Add your education details.")

    # Skills
    skills = [
        "python", "java", "c++", "html", "css",
        "javascript", "sql", "flask", "git"
    ]

    found = 0

    for skill in skills:
        if skill in text:
            found += 1

    score += min(found * 5, 25)

    if found < 4:
        suggestions.append("Add more technical skills.")

    # Projects
    if "project" in text:
        score += 15
    else:
        suggestions.append("Add your projects.")

    # Certifications
    if "certification" in text or "certificate" in text:
        score += 10
    else:
        suggestions.append("Add certifications.")

    # Experience
    if "experience" in text or "internship" in text:
        score += 15
    else:
        suggestions.append("Add internship or experience.")

    return score, suggestions