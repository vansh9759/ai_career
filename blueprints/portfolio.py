from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from database import db
from models import User, BuiltResume, VerifiedSkill, Resume

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/generator')
def generator():
    user_id = session.get('user_id', 1)
    user = User.query.get(user_id) or User.query.first()
    built_resume = BuiltResume.query.filter_by(user_id=user.id).first()
    uploaded_resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
    skills = VerifiedSkill.query.filter_by(user_id=user.id).all()
    
    return render_template(
        'portfolio/generator.html',
        user=user,
        resume=built_resume,
        uploaded_resume=uploaded_resume,
        skills=skills
    )

@portfolio_bp.route('/import-resume', methods=['POST'])
def import_resume():
    user_id = session.get('user_id', 1)
    user = User.query.get(user_id) or User.query.first()
    uploaded_resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
    
    if uploaded_resume and uploaded_resume.raw_text:
        # Sync profile info from resume
        user.bio = uploaded_resume.raw_text[:300] + "..."
        db.session.commit()
        flash("✨ Successfully imported resume data into your live Portfolio Website!", "success")
    else:
        flash("No uploaded resume found. Upload a resume first in the AI Resume Engine module.", "warning")
        
    return redirect(url_for('portfolio.generator'))

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
