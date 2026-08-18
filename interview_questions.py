def generate_questions(skills):

    questions = []

    skill_questions = {
        "Python": [
            "Explain the difference between a list and a tuple in Python.",
            "What are decorators in Python?"
        ],
        "Java": [
            "Explain the concept of OOP in Java.",
            "What is method overloading?"
        ],
        "C++": [
            "What is polymorphism in C++?",
            "Explain pointers in C++."
        ],
        "SQL": [
            "What is the difference between WHERE and HAVING?",
            "Explain JOIN types."
        ],
        "Flask": [
            "What is Flask?",
            "Explain Flask routing."
        ],
        "HTML": [
            "What is the difference between HTML and HTML5?"
        ],
        "CSS": [
            "Explain Flexbox and Grid."
        ],
        "JavaScript": [
            "Explain the difference between var, let and const."
        ],
        "Git": [
            "What is Git?",
            "Explain Git merge."
        ]
    }

    for skill in skills:
        if skill in skill_questions:
            questions.extend(skill_questions[skill])

    if not questions:
        questions.append("Tell me about yourself.")

    return questions