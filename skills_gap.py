import re

def analyze_skills_gap(resume_skills, job_description):

    words = re.findall(r'\b[a-zA-Z0-9+#.]+\b', job_description.lower())

    job_skills = set(words)
    resume_skills = set(skill.lower() for skill in resume_skills)

    matched = []
    missing = []

    for skill in sorted(job_skills):

        if skill in resume_skills:
            matched.append(skill)
        else:
            missing.append(skill)

    return matched, missing