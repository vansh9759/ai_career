from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from database import db
from models import Course, Lesson, User, RoadmapNodeProgress
from services.ai_engine import query_ai_engine
from services.scoring import DynamicScoringEngine

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/')
@learning_bp.route('/engine')
@learning_bp.route('/roadmap')
def engine():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id) if user_id else User.query.first()
    
    target_role = user.career_goal or "Full Stack AI Engineer" if user else "Full Stack AI Engineer"
    
    courses = Course.query.all()
    if not courses:
        c1 = Course(title="Complete Python for AI & Data Science", category="Artificial Intelligence", duration="12 Hours", difficulty="Beginner to Advanced", description="Master Python 3, NumPy, Pandas, Scikit-Learn and build production AI microservices.", skills_mapped="Python, Data Science, AI")
        c2 = Course(title="SQL & Relational Database Mastery", category="Databases", duration="8 Hours", difficulty="Intermediate", description="Complex queries, window functions, indexing, and database optimization for top tech companies.", skills_mapped="SQL, PostgreSQL, Databases")
        c3 = Course(title="System Design for High Scale Applications", category="System Design", duration="15 Hours", difficulty="Advanced", description="Microservices, Caching, Load Balancing, Message Queues, and Distributed Databases.", skills_mapped="System Design, Architecture, Microservices")
        db.session.add_all([c1, c2, c3])
        db.session.commit()
        courses = Course.query.all()

    # Dynamic interactive roadmap nodes
    roadmap_nodes = [
        {"id": 1, "title": "Phase 1: Programming Fundamentals & DSA", "weeks": "Weeks 1-3", "status": "Completed", "topics": ["Python 3", "Data Structures", "Algorithms", "Time Complexity"]},
        {"id": 2, "title": "Phase 2: Database Systems & SQL Optimization", "weeks": "Weeks 4-6", "status": "In Progress", "topics": ["PostgreSQL", "B-Tree Indexing", "Transactions & ACID", "Query Execution Plans"]},
        {"id": 3, "title": "Phase 3: Backend REST APIs & Microservices", "weeks": "Weeks 7-9", "status": "Locked", "topics": ["Flask / FastAPI", "JWT Auth & RBAC", "Docker Containerization", "Swagger/OpenAPI"]},
        {"id": 4, "title": "Phase 4: Large Language Models & AI Systems", "weeks": "Weeks 10-12", "status": "Locked", "topics": ["Prompt Engineering", "Vector DBs (Chroma/Qdrant)", "RAG Pipelines", "Fine-Tuning"]}
    ]

    node_progress_map = {}
    if user:
        progs = RoadmapNodeProgress.query.filter_by(user_id=user.id).all()
        for p in progs:
            node_progress_map[str(p.node_id)] = {
                "status": p.status,
                "notes": p.notes
            }

    return render_template(
        'learning/engine.html',
        user=user,
        target_role=target_role,
        courses=courses,
        roadmap_nodes=roadmap_nodes,
        node_progress_map=node_progress_map
    )

@learning_bp.route('/roadmap/node-status', methods=['POST'])
def update_node_status():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    node_id = str(data.get('node_id'))
    status = data.get('status', 'In Progress')
    notes = data.get('notes', '')

    prog = RoadmapNodeProgress.query.filter_by(user_id=user_id, node_id=node_id).first()
    if not prog:
        prog = RoadmapNodeProgress(user_id=user_id, node_id=node_id, status=status, notes=notes)
        db.session.add(prog)
    else:
        prog.status = status
        prog.notes = notes

    db.session.commit()
    DynamicScoringEngine.update_user_score(user_id)
    return jsonify({"success": True, "node_id": node_id, "status": status})

@learning_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course.id).all()
    if not lessons:
        l1 = Lesson(course_id=course.id, title="1. Introduction & Environment Setup", duration="10 mins", content_notes="Overview of environment configuration, IDE settings, and core concepts.")
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
    prompt = f"Student Question: {question}\nContext: {context}"
    ai_res = query_ai_engine(prompt, system_instruction="You are an expert Computer Science Professor and AI Mentor.")
    return jsonify({"answer": ai_res.get('text', 'Keep practicing!')})
