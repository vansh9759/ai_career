from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from database import db
from models import User, ProjectGeneratorResult
from services.ai_engine import query_ai_engine
from services.scoring import DynamicScoringEngine
from datetime import datetime

projects_bp = Blueprint('projects', __name__)

STATIC_PROJECTS = [
    {
        "id": 1,
        "title": "AI-Powered Customer Intelligence Engine",
        "level": "Advanced",
        "category": "AI & Full Stack",
        "tech_stack": "Python, Flask, React, PostgreSQL, Docker, Gemini API",
        "description": "Architect a real-time sentiment analysis and churn prediction SaaS microservice.",
        "architecture": "Client UI (React) -> Gateway API (Flask) -> LLM Inference Service (Gemini) -> DB Storage (PostgreSQL)",
        "db_schema": "Users(id, email), AnalyticsLogs(id, user_id, sentiment_score, prompt_tokens, created_at)",
        "api_routes": "POST /api/v1/analyze, GET /api/v1/metrics",
        "resume_bullets": "Engineered an AI customer intelligence pipeline utilizing Gemini API and Flask, achieving 94% sentiment accuracy across 50k+ user logs."
    },
    {
        "id": 2,
        "title": "Distributed Financial Trading Orderbook",
        "level": "Expert",
        "category": "System Design & C++",
        "tech_stack": "C++, Redis, WebSockets, Docker, React",
        "description": "Build a low-latency matching engine matching buy and sell orders in under 5ms.",
        "architecture": "Order Matching Core (C++) -> In-Memory Event Stream (Redis) -> WebSocket Server -> Dashboard UI",
        "db_schema": "Orders(id, user_id, symbol, price, quantity, side, status)",
        "api_routes": "POST /api/v1/orders, GET /api/v1/orderbook/depth",
        "resume_bullets": "Built high-frequency order matching engine in C++ executing 100k transactions per second with sub-5ms latency."
    }
]

@projects_bp.route('/')
@projects_bp.route('/builder')
def project_builder():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    saved_projects = ProjectGeneratorResult.query.filter_by(user_id=user_id).all() if user_id else []
    
    return render_template(
        'projects/builder.html',
        user=user,
        projects=STATIC_PROJECTS,
        saved_projects=saved_projects
    )

@projects_bp.route('/generate', methods=['POST'])
def generate_project():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to generate custom AI project blueprints.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    domain = request.form.get('domain', 'Full Stack AI').strip()
    tech_stack = request.form.get('tech_stack', 'Python, React, PostgreSQL').strip()
    difficulty = request.form.get('difficulty', 'Intermediate').strip()

    prompt = f"""
    Generate an enterprise project blueprint for a candidate targeting '{user.dream_job or 'Software Engineer'}' at '{user.dream_company or 'Top Tech'}'.
    Domain: {domain}
    Tech Stack: {tech_stack}
    Difficulty: {difficulty}

    Return structured JSON with keys:
    - "title": catchy technical project title
    - "description": 2-sentence product summary
    - "tech_stack": full tech stack
    - "architecture": system flow diagram summary
    - "db_schema": main tables and relationships
    - "api_routes": key REST API endpoints
    - "phases": list of 4 development phases
    - "readme_markdown": complete GitHub README markdown snippet
    """

    ai_res = query_ai_engine(prompt, system_instruction="You are a Principal Software Architect.")

    title = f"{domain} Enterprise SaaS ({difficulty})"
    tech_stack_str = tech_stack
    architecture_str = "Client (React/HTML5) -> Server API (Flask/Python) -> DB (PostgreSQL/Redis)"
    db_schema_str = "Users, Tasks, Analytics, Credentials, AuditLogs"
    api_routes_str = "POST /api/v1/action, GET /api/v1/dashboard"
    readme_str = f"# {title}\n\n## Stack\n{tech_stack_str}\n\n## Architecture\n{architecture_str}\n\n## API\n{api_routes_str}"

    p_res = ProjectGeneratorResult(
        user_id=user_id,
        title=title,
        tech_stack=tech_stack_str,
        architecture=architecture_str,
        db_schema=db_schema_str,
        api_routes=api_routes_str,
        readme_markdown=readme_str,
        created_at=datetime.utcnow()
    )
    db.session.add(p_res)
    db.session.commit()

    DynamicScoringEngine.update_user_score(user_id)
    flash(f"✨ AI Project Blueprint '{title}' successfully generated & added to your portfolio!", "success")
    return redirect(url_for('projects.project_builder'))
