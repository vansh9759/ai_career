from flask import Blueprint, render_template, request, session
from database import db
from models import User, BuiltResume, VerifiedSkill

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/generator')
def generator():
    user_id = session.get('user_id', 1)
    user = User.query.get(user_id) or User.query.first()
    built_resume = BuiltResume.query.filter_by(user_id=user.id).first()
    skills = VerifiedSkill.query.filter_by(user_id=user.id).all()
    return render_template('portfolio/generator.html', user=user, resume=built_resume, skills=skills)

@portfolio_bp.route('/linkedin-optimizer', methods=['GET', 'POST'])
def linkedin_optimizer():
    optimized = None
    if request.method == 'POST':
        headline = request.form.get('headline', '')
        about = request.form.get('about', '')
        optimized = {
            "headline": "Software Engineer @ AI Career OS | Python, SQL & React Specialist | Building Scalable Cloud & AI Services",
            "about": "Passionate Software Engineer with a proven track record of solving complex algorithmic problems and delivering high-impact SaaS applications. Specialized in Python, Relational Databases, and RESTful Microservice Architecture.",
            "tips": [
                "Include key technical keywords in your headline for maximum search visibility.",
                "Quantify achievements in your Experience section using numbers and percentages."
            ]
        }
    return render_template('portfolio/linkedin_optimizer.html', optimized=optimized)
