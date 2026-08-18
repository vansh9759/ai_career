from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import db
from models import User, EmployabilityScore, VerifiedSkill, CodingSubmission, MockInterviewSession, JobApplication, GamificationProfile
from services.ai_engine import AICareerEngine

student_bp = Blueprint('student', __name__)

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@student_bp.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        # Default mock demo user if guest
        user = User.query.first()
        if not user:
            return redirect(url_for('auth.login'))

    emp_record = EmployabilityScore.query.filter_by(user_id=user.id).first()
    if not emp_record:
        emp_record = EmployabilityScore(user_id=user.id, total_score=68)
        db.session.add(emp_record)
        db.session.commit()

    emp_data = AICareerEngine.calculate_employability_index(user, emp_record)
    company_readiness = AICareerEngine.calculate_company_readiness(user.dream_company, emp_data['total_score'])
    
    verified_skills = VerifiedSkill.query.filter_by(user_id=user.id).all()
    recent_submissions = CodingSubmission.query.filter_by(user_id=user.id).order_by(CodingSubmission.submitted_at.desc()).limit(5).all()
    mock_interviews = MockInterviewSession.query.filter_by(user_id=user.id).limit(3).all()
    applications = JobApplication.query.filter_by(user_id=user.id).limit(5).all()
    gamification = GamificationProfile.query.filter_by(user_id=user.id).first()

    return render_template(
        'student_dashboard.html',
        user=user,
        emp_data=emp_data,
        company_readiness=company_readiness,
        verified_skills=verified_skills,
        recent_submissions=recent_submissions,
        mock_interviews=mock_interviews,
        applications=applications,
        gamification=gamification
    )

@student_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user = get_current_user()
    if not user:
        user = User.query.first()

    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.dream_company = request.form.get('dream_company', user.dream_company)
        user.dream_job = request.form.get('dream_job', user.dream_job)
        user.career_goal = request.form.get('career_goal', user.career_goal)
        user.college = request.form.get('college', user.college)
        user.degree = request.form.get('degree', user.degree)
        user.github = request.form.get('github', user.github)
        user.linkedin = request.form.get('linkedin', user.linkedin)
        user.leetcode = request.form.get('leetcode', user.leetcode)
        user.hackerrank = request.form.get('hackerrank', user.hackerrank)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', user=user)

@student_bp.route('/readiness')
def readiness():
    user = get_current_user()
    if not user:
        user = User.query.first()
    
    emp_record = EmployabilityScore.query.filter_by(user_id=user.id).first()
    score = emp_record.total_score if emp_record else 68

    companies = ['Google', 'Microsoft', 'Amazon', 'Meta', 'NVIDIA', 'Apple', 'Adobe', 'Netflix', 'Oracle', 'TCS', 'Infosys', 'Wipro']
    readiness_list = [AICareerEngine.calculate_company_readiness(c, score) for c in companies]

    return render_template('student/readiness.html', user=user, readiness_list=readiness_list)
