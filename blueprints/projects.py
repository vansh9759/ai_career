from flask import Blueprint, render_template, request, jsonify
from database import db
from models import ProjectBlueprint

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/builder')
def project_builder():
    projects = [
        {
            "id": 1,
            "title": "AI-Powered Customer Intelligence Engine",
            "level": "Advanced",
            "category": "AI & Full Stack",
            "tech_stack": "Python, Flask, React, PostgreSQL, Docker, Gemini API",
            "description": "Architect a real-time sentiment analysis and churn prediction SaaS microservice.",
            "architecture": "Client UI (React) -> Gateway API (Flask) -> LLM Inference Service (Gemini) -> DB Storage (PostgreSQL)",
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
            "resume_bullets": "Built high-frequency order matching engine in C++ executing 100k transactions per second with sub-5ms latency."
        }
    ]
    return render_template('projects/builder.html', projects=projects)
