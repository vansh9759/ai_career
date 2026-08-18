from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database import db
from models import Course, Lesson, User
from services.ai_engine import AICareerEngine

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/engine')
def engine():
    user_id = session.get('user_id', 1)
    user = User.query.get(user_id) or User.query.first()
    
    roadmap = AICareerEngine.generate_career_roadmap(user.career_goal if user else "AI Engineer")
    courses = Course.query.all()

    if not courses:
        # Seed default course catalog
        c1 = Course(title="Complete Python for AI & Data Science", category="Artificial Intelligence", duration="12 Hours", difficulty="Beginner to Advanced", description="Master Python 3, NumPy, Pandas, Scikit-Learn and build production AI microservices.", skills_mapped="Python, Data Science, AI")
        c2 = Course(title="SQL & Relational Database Mastery", category="Databases", duration="8 Hours", difficulty="Intermediate", description="Complex queries, window functions, indexing, and database optimization for top tech companies.", skills_mapped="SQL, PostgreSQL, Databases")
        c3 = Course(title="System Design for High Scale Applications", category="System Design", duration="15 Hours", difficulty="Advanced", description="Microservices, Caching, Load Balancing, Message Queues, and Distributed Databases.", skills_mapped="System Design, Architecture, Microservices")
        db.session.add_all([c1, c2, c3])
        db.session.commit()
        courses = Course.query.all()

    return render_template('learning/engine.html', user=user, roadmap=roadmap, courses=courses)

@learning_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course.id).all()
    if not lessons:
        l1 = Lesson(course_id=course.id, title="1. Introduction & Course Setup", duration="10 mins", content_notes="Overview of environment configuration, IDE settings, and core concepts.")
        l2 = Lesson(course_id=course.id, title="2. Core Concepts & Practical Implementation", duration="25 mins", content_notes="Hands-on coding exercise building your first module.")
        db.session.add_all([l1, l2])
        db.session.commit()
        lessons = Lesson.query.filter_by(course_id=course.id).all()

    return render_template('learning/course_detail.html', course=course, lessons=lessons)

@learning_bp.route('/ask-doubt', methods=['POST'])
def ask_doubt():
    data = request.get_json() or {}
    question = data.get('question', '')
    context = data.get('context', '')
    answer = AICareerEngine.ask_ai_mentor(question, context)
    return jsonify({"answer": answer})
