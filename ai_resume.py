def improve_resume(resume_text):

    print("===== improve_resume() CALLED =====")

    prompt = f"""
You are an Expert HR Recruiter, ATS Resume Reviewer, ATS Scanner, and Professional Resume Writer.

Analyze the following resume carefully.

Generate a professional report using EXACTLY the following headings.

# ⭐ RESUME SCORE
Give an ATS score out of 100.

# ✅ STRENGTHS
Write 5 strengths.

# ⚠️ WEAKNESSES
Write 5 weaknesses.

# 🚀 ATS IMPROVEMENTS
Explain how to improve ATS score.

# ✨ IMPROVED CAREER OBJECTIVE
Rewrite the objective professionally.

# 💻 IMPROVED TECHNICAL SKILLS
Rewrite the skills professionally and add missing skills.

# 📂 IMPROVED PROJECT DESCRIPTION
Rewrite the project professionally.

# 👔 IMPROVED EXPERIENCE
Rewrite the experience professionally.

# 📜 RECOMMENDED CERTIFICATIONS
Recommend certifications.

# 🎯 CAREER ADVICE
Give career advice.

Resume:

{resume_text}

IMPORTANT:
Return ONLY the report.
Do NOT return a Python list.
Do NOT return JSON.
Do NOT use [] brackets.
Do NOT use bullet list syntax like ['...'].
Return plain formatted text.
"""

    try:

        response = model.generate_content(prompt)

        ai_text = response.text.strip()

        print("\n========== GEMINI RESPONSE ==========\n")
        print(ai_text)
        print(type(ai_text))
        print("\n=====================================\n")

        return ai_text

    except Exception as e:

        print("Gemini Error:", e)

        return f"Error: {e}"