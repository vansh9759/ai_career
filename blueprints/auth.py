from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User, EmployabilityScore, GamificationProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash('Logged in successfully!', 'success')
            
            if user.role == 'recruiter' or user.role == 'company':
                return redirect(url_for('recruiter.dashboard'))
            elif user.role == 'university':
                return redirect(url_for('university.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'student').strip()
        dream_company = request.form.get('dream_company', 'Google').strip()

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('auth.login'))

        hashed_pw = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_pw,
            role=role,
            dream_company=dream_company
        )
        db.session.add(new_user)
        db.session.commit()

        # Initialize EmployabilityScore & GamificationProfile for student
        if role == 'student':
            emp_score = EmployabilityScore(user_id=new_user.id, total_score=68)
            gam_prof = GamificationProfile(user_id=new_user.id, xp=100, coins=50)
            db.session.add(emp_score)
            db.session.add(gam_prof)
            db.session.commit()

        session['user_id'] = new_user.id
        session['user_name'] = new_user.name
        session['user_role'] = new_user.role
        flash('Account created successfully!', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))
