from flask import Blueprint, render_template, request, session
from database import db
from models import User, EmployabilityScore, VerifiedSkill, JobPosting

recruiter_bp = Blueprint('recruiter', __name__)

@recruiter_bp.route('/dashboard')
def dashboard():
    candidates = User.query.filter_by(role='student').all()
    if not candidates:
        # Mock top candidates
        candidates = [User.query.first()] if User.query.first() else []

    top_candidates = []
    for c in candidates:
        emp = EmployabilityScore.query.filter_by(user_id=c.id).first()
        skills = VerifiedSkill.query.filter_by(user_id=c.id).all()
        score = emp.total_score if emp else 75
        top_candidates.append({
            "user": c,
            "employability_score": score,
            "verified_skills": [s.skill_name for s in skills] or ["Python", "SQL", "React"],
            "match_reason": "Top 5% in Python Coding Arena and 92 ATS Resume Score"
        })

    # Sort candidates by Employability Index score descending
    top_candidates.sort(key=lambda x: x['employability_score'], reverse=True)

    return render_template('recruiter/dashboard.html', top_candidates=top_candidates)
