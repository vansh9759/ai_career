import re

SKILLS = [

    # Programming Languages
    "python", "java", "c", "c++", "c#", "javascript",
    "typescript", "php", "go", "ruby", "swift", "kotlin",

    # Web Development
    "html", "css", "bootstrap", "tailwind",
    "react", "angular", "vue", "next.js",
    "node.js", "express", "flask", "django",
    "fastapi",

    # Database
    "sql", "mysql", "postgresql", "mongodb",
    "sqlite", "oracle",

    # AI / ML
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "tensorflow",
    "keras",
    "pytorch",
    "opencv",
    "numpy",
    "pandas",
    "scikit-learn",

    # Cloud
    "aws",
    "azure",
    "google cloud",

    # DevOps
    "docker",
    "kubernetes",
    "git",
    "github",
    "gitlab",
    "jenkins",

    # Tools
    "linux",
    "postman",
    "vscode",
    "visual studio",
    "figma",

    # Mobile
    "android",
    "flutter",

    # Others
    "rest api",
    "firebase",
    "spring boot",
    "power bi",
    "tableau"
]


def extract_email(text):
    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    return match.group() if match else "Not Found"


def extract_phone(text):
    match = re.search(
        r"(\+91[- ]?)?[6-9]\d{9}",
        text
    )

    return match.group() if match else "Not Found"


def extract_name(text):

    for line in text.split("\n"):

        line = line.strip()

        if line and len(line.split()) <= 4:
            return line

    return "Not Found"


def extract_skills(text):

    text = text.lower()

    detected = []

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text):
            detected.append(skill.title())

    return sorted(list(set(detected)))