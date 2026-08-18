def generate_ai_suggestions(text):

    text = text.lower()

    suggestions = []

    if "github" not in text:
        suggestions.append("Add your GitHub profile.")

    if "linkedin" not in text:
        suggestions.append("Add your LinkedIn profile.")

    if "internship" not in text:
        suggestions.append("Mention internship experience.")

    if "project" not in text:
        suggestions.append("Add more project details.")

    if "certification" not in text and "certificate" not in text:
        suggestions.append("Include certifications.")

    if "achievement" not in text:
        suggestions.append("Mention achievements or awards.")

    if "objective" not in text:
        suggestions.append("Add a career objective.")

    if len(suggestions) == 0:
        suggestions.append("Excellent resume. No major improvements required.")

    return suggestions