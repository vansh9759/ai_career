def calculate_resume_strength(resume_data):
    score = 0
    suggestions = []

    required_fields = [
        "name",
        "email",
        "phone",
        "career_objective",
        "college",
        "degree",
        "skills",
        "projects",
        "experience",
        "certifications",
        "achievements",
        "languages"
    ]

    for field in required_fields:
        value = resume_data.get(field)

        if value:
            score += 8
        else:
            suggestions.append(f"Add {field.replace('_', ' ').title()}")

    if score >= 90:
        level = "Excellent"
    elif score >= 75:
        level = "Good"
    elif score >= 60:
        level = "Average"
    else:
        level = "Needs Improvement"

    return score, level, suggestions