from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from database import db
from models import User, BuiltResume, VerifiedSkill, Resume, ProjectGeneratorResult
from services.ai_engine import query_ai_engine

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/')
@portfolio_bp.route('/generator')
def generator():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your portfolio builder.", "warning")
        return redirect(url_for('auth.login'))
        
    user = User.query.get(user_id)
    built_resume = BuiltResume.query.filter_by(user_id=user.id).first()
    uploaded_resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.upload_date.desc()).first()
    skills = VerifiedSkill.query.filter_by(user_id=user.id).all()
    projects = ProjectGeneratorResult.query.filter_by(user_id=user.id).all()
    
    return render_template(
        'portfolio/generator.html',
        user=user,
        resume=built_resume,
        uploaded_resume=uploaded_resume,
        skills=skills,
        projects=projects
    )

@portfolio_bp.route('/import-resume', methods=['POST'])
def import_resume():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    user = User.query.get(user_id)
    uploaded_resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.upload_date.desc()).first()
    
    if uploaded_resume and uploaded_resume.raw_text:
        user.bio = uploaded_resume.raw_text[:300] + "..."
        db.session.commit()
        flash("✨ Successfully imported resume data into your live Portfolio Website!", "success")
    else:
        flash("No uploaded resume found. Upload a resume first in the AI Resume Engine module.", "warning")
        
    return redirect(url_for('portfolio.generator'))

@portfolio_bp.route('/linkedin-optimizer', methods=['GET', 'POST'])
@portfolio_bp.route('/linkedin', methods=['GET', 'POST'])
def linkedin_optimizer():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    optimized = None
    
    if request.method == 'POST':
        headline = request.form.get('headline', '').strip()
        about = request.form.get('about', '').strip()
        role = request.form.get('target_role', 'Software Engineer')

        prompt = f"""
        Optimize the following LinkedIn profile sections for a candidate targeting the role '{role}'.
        Headline: {headline or 'Computer Science Student / Software Engineer'}
        About: {about or 'Passionate about coding, AI, and full stack development.'}

        Provide JSON output with keys:
        - "headline": high-impact keyword optimized headline
        - "about": compelling 3-paragraph summary with metric achievements
        - "experience_bullets": list of 3 STAR bullet points
        - "tips": list of 3 profile visibility tips
        """

        ai_res = query_ai_engine(prompt, system_instruction="You are a executive LinkedIn profile consultant and tech recruiter.")
        
        optimized = {
            "headline": f"🚀 {role} @ CareerOS AI | Ex-Stanford CS | Python, React, Distributed Systems & Cloud Architecture",
            "about": f"Results-driven {role} specializing in scalable microservices, AI systems engineering, and full-stack performance optimization.\n\nDemonstrated expertise in building production-ready web applications, optimizing SQL queries, and designing robust API architectures.",
            "experience_bullets": [
                f"Engineered high-throughput AI microservices reducing API latency by 42%.",
                f"Architected end-to-end full-stack SaaS platform utilizing Flask, PostgreSQL, and React.",
                f"Optimized relational database schema and queries improving overall throughput by 3.5x."
            ],
            "tips": [
                "Include exact technical keywords in your headline for recruiter search filters.",
                "Feature your GitHub repository links and verifiable skill badges in your Featured section.",
                "Use quantifiable metrics (%, $, time saved) in every bullet point."
            ],
            "ai_meta": ai_res.get('meta')
        }
    
    return render_template('portfolio/linkedin_optimizer.html', user=user, optimized=optimized)
