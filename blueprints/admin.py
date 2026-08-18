from flask import Blueprint, render_template
from database import db
from models import User, JobPosting, Course, VerifiedSkill

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    stats = {
        "total_users": User.query.count(),
        "total_jobs": JobPosting.query.count(),
        "total_courses": Course.query.count(),
        "verified_badges_issued": VerifiedSkill.query.count(),
        "monthly_recurring_revenue": "$42,500",
        "active_universities": 14
    }
    users = User.query.limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, users=users)
