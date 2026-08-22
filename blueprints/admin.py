from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models import User, JobPosting, Course, VerifiedSkill, EmployabilityScore, CodingChallenge
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    user_id = session.get('user_id', 1)
    current_user_obj = User.query.get(user_id) or User.query.first()

    stats = {
        "total_users": User.query.count(),
        "total_jobs": JobPosting.query.count(),
        "total_courses": Course.query.count(),
        "total_coding_challenges": CodingChallenge.query.count(),
        "verified_badges_issued": VerifiedSkill.query.count(),
        "monthly_recurring_revenue": "$42,500",
        "active_universities": 14
    }
    
    users = User.query.order_by(User.created_at.desc()).all()
    jobs = JobPosting.query.order_by(JobPosting.posted_at.desc()).all()
    badges = VerifiedSkill.query.order_by(VerifiedSkill.verified_at.desc()).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        users=users,
        jobs=jobs,
        badges=badges,
        user=current_user_obj
    )

@admin_bp.route('/change-role/<int:target_user_id>', methods=['POST'])
def change_role(target_user_id):
    new_role = request.form.get('role', 'student')
    target_user = User.query.get_or_404(target_user_id)
    target_user.role = new_role
    db.session.commit()
    flash(f"Updated role for {target_user.name} to '{new_role}'.", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete-user/<int:target_user_id>', methods=['POST'])
def delete_user(target_user_id):
    target_user = User.query.get_or_404(target_user_id)
    name = target_user.name
    
    # Delete related records
    EmployabilityScore.query.filter_by(user_id=target_user_id).delete()
    VerifiedSkill.query.filter_by(user_id=target_user_id).delete()
    User.query.filter_by(id=target_user_id).delete()
    
    db.session.commit()
    flash(f"User '{name}' has been deleted from the platform.", "warning")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/create-job', methods=['POST'])
def create_job():
    company = request.form.get('company', 'Enterprise HR')
    title = request.form.get('title', 'Software Engineer')
    location = request.form.get('location', 'Remote')
    salary_range = request.form.get('salary_range', '$120,000 - $150,000')
    requirements = request.form.get('requirements', 'Python, SQL, React')
    
    job = JobPosting(
        company=company,
        title=title,
        location=location,
        salary_range=salary_range,
        requirements=requirements,
        min_employability_score=75
    )
    db.session.add(job)
    db.session.commit()
    
    flash(f"🎉 New Job Opportunity '{title}' at {company} published live!", "success")
    return redirect(url_for('admin.dashboard'))
