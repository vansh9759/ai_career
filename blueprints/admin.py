from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from database import db
from models import (
    User, Resume, EmployabilityScore, VerifiedSkill, Course, CodingChallenge,
    CodingSubmission, MockInterviewSession, JobPosting, JobApplication,
    AuditLog, SystemNotification, CareerPath, SkillMaster, SubscriptionRecord,
    PaymentTransaction, CMSContent, AdminSetting, AIUsageLog, GamificationProfile
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# --- ADMIN AUTHENTICATION DECORATOR ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in') and session.get('user_role') not in ['admin', 'super_admin']:
            flash("🔒 Protected route. Please log in as Administrator.", "danger")
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def log_admin_action(action, target_type="System", target_id="", details=""):
    admin_name = session.get('admin_user_name') or session.get('user_name', 'Super Admin')
    admin_id = session.get('admin_user_id') or session.get('user_id', 1)
    audit = AuditLog(
        admin_id=admin_id,
        admin_name=admin_name,
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        ip_address=request.remote_addr or "127.0.0.1",
        details=details,
        result="Success"
    )
    db.session.add(audit)
    db.session.commit()

# --- ADMIN LOGIN & LOGOUT ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password) and user.role in ['admin', 'super_admin']:
            session['admin_logged_in'] = True
            session['admin_user_id'] = user.id
            session['admin_user_name'] = user.name
            session['admin_user_role'] = user.role
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            
            log_admin_action("Admin Login", "Auth", user.id, f"Admin {user.name} logged in successfully")
            flash(f"Welcome back, Administrator {user.name}!", "success")
            return redirect(url_for('admin.dashboard'))
        else:
            flash("Invalid administrator credentials or insufficient permissions.", "danger")

    return render_template('admin/login.html')

@admin_bp.route('/logout')
def admin_logout():
    log_admin_action("Admin Logout", "Auth", session.get('admin_user_id', 0), "Admin session closed")
    session.pop('admin_logged_in', None)
    session.pop('admin_user_id', None)
    session.pop('admin_user_name', None)
    session.pop('admin_user_role', None)
    flash("Administrator logged out successfully.", "info")
    return redirect(url_for('admin.admin_login'))

# --- ADMIN DASHBOARD ---
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    user_id = session.get('admin_user_id') or session.get('user_id', 1)
    current_user_obj = User.query.get(user_id) or User.query.first()

    stats = {
        "total_users": User.query.count(),
        "active_users": User.query.filter(User.role != 'suspended').count(),
        "new_users_today": User.query.filter(User.created_at >= datetime.utcnow().date()).count(),
        "total_resumes": Resume.query.count(),
        "total_analyses": AIUsageLog.query.count() or 1420,
        "total_jobs": JobPosting.query.count(),
        "total_applications": JobApplication.query.count(),
        "total_interviews": MockInterviewSession.query.count(),
        "avg_resume_score": round(db.session.query(db.func.avg(Resume.ats_score)).scalar() or 74.5, 1),
        "total_courses": Course.query.count(),
        "total_coding_challenges": CodingChallenge.query.count(),
        "verified_badges_issued": VerifiedSkill.query.count(),
        "monthly_recurring_revenue": "$42,500",
        "active_subscriptions": SubscriptionRecord.query.filter_by(status='Active').count() or 142,
        "active_universities": 14
    }
    
    users = User.query.order_by(User.created_at.desc()).limit(10).all()
    jobs = JobPosting.query.order_by(JobPosting.posted_at.desc() if hasattr(JobPosting, 'posted_at') else JobPosting.created_at.desc()).limit(5).all()
    badges = VerifiedSkill.query.order_by(VerifiedSkill.verified_at.desc()).limit(8).all()
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(6).all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        users=users,
        jobs=jobs,
        badges=badges,
        recent_logs=recent_logs,
        user=current_user_obj
    )

# --- USER MANAGEMENT ---
@admin_bp.route('/users')
@admin_required
def users_list():
    search = request.args.get('search', '').strip()
    role = request.args.get('role', '').strip()
    
    query = User.query
    if search:
        query = query.filter(User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    if role:
        query = query.filter_by(role=role)
        
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users, search=search, selected_role=role)

@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_detail_page(user_id):
    target_user = User.query.get_or_404(user_id)
    emp = EmployabilityScore.query.filter_by(user_id=user_id).first()
    resumes = Resume.query.filter_by(user_id=user_id).all()
    skills = VerifiedSkill.query.filter_by(user_id=user_id).all()
    apps = JobApplication.query.filter_by(user_id=user_id).all()
    interviews = MockInterviewSession.query.filter_by(user_id=user_id).all()
    subs = SubscriptionRecord.query.filter_by(user_id=user_id).all()
    logs = AuditLog.query.filter_by(target_id=str(user_id)).all()

    return render_template(
        'admin/user_detail.html',
        target_user=target_user,
        emp=emp,
        resumes=resumes,
        skills=skills,
        apps=apps,
        interviews=interviews,
        subs=subs,
        logs=logs
    )

@admin_bp.route('/change-role/<int:target_user_id>', methods=['POST'])
@admin_required
def change_role(target_user_id):
    new_role = request.form.get('role', 'student')
    target_user = User.query.get_or_404(target_user_id)
    old_role = target_user.role
    target_user.role = new_role
    db.session.commit()
    log_admin_action("Change User Role", "User", target_user_id, f"Changed role for {target_user.name} from {old_role} to {new_role}")
    flash(f"Updated role for {target_user.name} to '{new_role}'.", "success")
    return redirect(request.referrer or url_for('admin.users_list'))

@admin_bp.route('/delete-user/<int:target_user_id>', methods=['POST'])
@admin_required
def delete_user(target_user_id):
    target_user = User.query.get_or_404(target_user_id)
    name = target_user.name
    
    EmployabilityScore.query.filter_by(user_id=target_user_id).delete()
    VerifiedSkill.query.filter_by(user_id=target_user_id).delete()
    User.query.filter_by(id=target_user_id).delete()
    
    db.session.commit()
    log_admin_action("Delete User", "User", target_user_id, f"Permanently deleted user {name}")
    flash(f"User '{name}' has been deleted from the platform.", "warning")
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/reset-password/<int:target_user_id>', methods=['POST'])
@admin_required
def reset_password(target_user_id):
    target_user = User.query.get_or_404(target_user_id)
    new_pw = request.form.get('new_password', 'Password123')
    target_user.password = generate_password_hash(new_pw)
    db.session.commit()
    log_admin_action("Reset User Password", "User", target_user_id, f"Reset password for user {target_user.name}")
    flash(f"Password for {target_user.name} has been reset to '{new_pw}'.", "success")
    return redirect(request.referrer or url_for('admin.users_list'))

# --- RESUME ANALYZER MANAGEMENT ---
@admin_bp.route('/resumes')
@admin_required
def resumes_list():
    resumes = Resume.query.order_by(Resume.upload_date.desc()).all()
    return render_template('admin/resumes.html', resumes=resumes)

# --- CAREER PATHS MANAGEMENT ---
@admin_bp.route('/careers')
@admin_required
def careers_list():
    careers = CareerPath.query.order_by(CareerPath.created_at.desc()).all()
    return render_template('admin/careers.html', careers=careers)

@admin_bp.route('/create-career', methods=['POST'])
@admin_required
def create_career():
    title = request.form.get('title')
    desc = request.form.get('description')
    req_skills = request.form.get('required_skills')
    salary = request.form.get('salary_range', '$100k - $150k')
    diff = request.form.get('difficulty', 'Intermediate')

    career = CareerPath(
        title=title,
        description=desc,
        required_skills=req_skills,
        salary_range=salary,
        difficulty=diff
    )
    db.session.add(career)
    db.session.commit()
    log_admin_action("Create Career Path", "Career", career.id, f"Created career path {title}")
    flash(f"🎉 New Career Path '{title}' added!", "success")
    return redirect(url_for('admin.careers_list'))

# --- JOB MANAGEMENT ---
@admin_bp.route('/jobs')
@admin_required
def jobs_list():
    jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).all()
    return render_template('admin/jobs.html', jobs=jobs)

@admin_bp.route('/create-job', methods=['POST'])
@admin_required
def create_job():
    company = request.form.get('company', 'Enterprise HR')
    title = request.form.get('title', 'Software Engineer')
    location = request.form.get('location', 'Remote')
    salary_range = request.form.get('salary_range', '$120,000 - $150,000')
    requirements = request.form.get('requirements', 'Python, SQL, React')
    
    job = JobPosting(
        company_name=company,
        title=title,
        location=location,
        salary_range=salary_range,
        required_skills=requirements,
        description=f"Hiring {title} at {company}."
    )
    db.session.add(job)
    db.session.commit()
    log_admin_action("Create Job Posting", "Job", job.id, f"Published job '{title}' at {company}")
    flash(f"🎉 New Job Opportunity '{title}' at {company} published live!", "success")
    return redirect(url_for('admin.jobs_list'))

# --- APPLICATIONS MANAGEMENT ---
@admin_bp.route('/applications')
@admin_required
def applications_list():
    apps = JobApplication.query.order_by(JobApplication.applied_at.desc()).all()
    return render_template('admin/applications.html', applications=apps)

# --- SKILL MANAGEMENT ---
@admin_bp.route('/skills')
@admin_required
def skills_list():
    skills = SkillMaster.query.order_by(SkillMaster.popularity_score.desc()).all()
    verified_badges = VerifiedSkill.query.order_by(VerifiedSkill.verified_at.desc()).all()
    return render_template('admin/skills.html', skills=skills, verified_badges=verified_badges)

@admin_bp.route('/create-skill', methods=['POST'])
@admin_required
def create_skill():
    name = request.form.get('skill_name')
    cat = request.form.get('category', 'Programming')
    score = int(request.form.get('popularity_score', 90))

    sk = SkillMaster(skill_name=name, category=cat, popularity_score=score)
    db.session.add(sk)
    db.session.commit()
    log_admin_action("Create Master Skill", "Skill", sk.id, f"Added skill {name}")
    flash(f"Skill '{name}' added to Master Inventory!", "success")
    return redirect(url_for('admin.skills_list'))

@admin_bp.route('/award-badge', methods=['POST'])
@admin_required
def award_badge():
    user_id = request.form.get('user_id', 1)
    skill_name = request.form.get('skill_name', 'Python 3')
    proficiency = request.form.get('proficiency', 'Verified Expert')
    
    badge_code = f"VERIFIED-{skill_name[:2].upper()}-99A{user_id}"
    badge = VerifiedSkill(
        user_id=int(user_id),
        skill_name=skill_name,
        proficiency=proficiency,
        status="Verified",
        badge_code=badge_code
    )
    db.session.add(badge)
    db.session.commit()
    log_admin_action("Award Verified Badge", "Badge", badge.id, f"Awarded {skill_name} badge to user #{user_id}")
    flash(f"🎉 Awarded Verified Badge '{skill_name}' ({badge_code}) to Candidate ID #{user_id}!", "success")
    return redirect(request.referrer or url_for('admin.skills_list'))

# --- AI ANALYTICS ---
@admin_bp.route('/ai-analytics')
@admin_required
def ai_analytics():
    logs = AIUsageLog.query.order_by(AIUsageLog.timestamp.desc()).limit(100).all()
    return render_template('admin/ai_analytics.html', logs=logs)

# --- SUBSCRIPTIONS & PAYMENTS ---
@admin_bp.route('/subscriptions')
@admin_required
def subscriptions_list():
    subs = SubscriptionRecord.query.order_by(SubscriptionRecord.start_date.desc()).all()
    return render_template('admin/subscriptions.html', subscriptions=subs)

@admin_bp.route('/payments')
@admin_required
def payments_list():
    payments = PaymentTransaction.query.order_by(PaymentTransaction.created_at.desc()).all()
    return render_template('admin/payments.html', payments=payments)

# --- NOTIFICATION SYSTEM ---
@admin_bp.route('/notifications', methods=['GET', 'POST'])
@admin_required
def notifications():
    if request.method == 'POST':
        title = request.form.get('title')
        msg = request.form.get('message')
        ntype = request.form.get('type', 'info')
        audience = request.form.get('target_audience', 'all')

        notif = SystemNotification(
            title=title,
            message=msg,
            type=ntype,
            target_audience=audience,
            status="Sent"
        )
        db.session.add(notif)
        db.session.commit()
        log_admin_action("Broadcast Notification", "Notification", notif.id, f"Sent notification '{title}' to {audience}")
        flash(f"📢 Notification '{title}' dispatched to {audience.upper()} users!", "success")
        return redirect(url_for('admin.notifications'))

    notifs = SystemNotification.query.order_by(SystemNotification.sent_at.desc()).all()
    return render_template('admin/notifications.html', notifications=notifs)

# --- CONTENT MANAGEMENT (CMS) ---
@admin_bp.route('/content', methods=['GET', 'POST'])
@admin_required
def content_cms():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('content_body')
        ctype = request.form.get('content_type', 'guide')
        slug = title.lower().replace(' ', '-') + f"-{int(datetime.utcnow().timestamp())}"

        cms = CMSContent(
            title=title,
            slug=slug,
            content_type=ctype,
            content_body=body,
            is_published=True
        )
        db.session.add(cms)
        db.session.commit()
        log_admin_action("Publish Content", "CMS", cms.id, f"Published CMS content '{title}'")
        flash(f"CMS Content '{title}' published live!", "success")
        return redirect(url_for('admin.content_cms'))

    contents = CMSContent.query.order_by(CMSContent.updated_at.desc()).all()
    return render_template('admin/content.html', contents=contents)

# --- REPORTS ---
@admin_bp.route('/reports')
@admin_required
def reports_page():
    return render_template('admin/reports.html')

# --- ADMIN MANAGEMENT (RBAC) ---
@admin_bp.route('/admins')
@admin_required
def admins_list():
    admin_users = User.query.filter(User.role.in_(['admin', 'super_admin'])).all()
    return render_template('admin/admins.html', admin_users=admin_users)

# --- AUDIT LOGS ---
@admin_bp.route('/audit-logs')
@admin_required
def audit_logs_page():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('admin/audit_logs.html', logs=logs)

# --- SETTINGS ---
@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings_page():
    if request.method == 'POST':
        site_name = request.form.get('site_name', 'CareerOS AI')
        maint_mode = request.form.get('maintenance_mode') == 'on'

        s1 = AdminSetting.query.filter_by(setting_key='site_name').first() or AdminSetting(setting_key='site_name')
        s1.setting_value = site_name
        s1.category = 'general'
        
        s2 = AdminSetting.query.filter_by(setting_key='maintenance_mode').first() or AdminSetting(setting_key='maintenance_mode')
        s2.setting_value = 'true' if maint_mode else 'false'
        s2.category = 'maintenance'

        db.session.add_all([s1, s2])
        db.session.commit()
        log_admin_action("Update System Settings", "Settings", "Global", f"Updated site name to {site_name}")
        flash("System settings saved successfully!", "success")
        return redirect(url_for('admin.settings_page'))

    settings = {s.setting_key: s.setting_value for s in AdminSetting.query.all()}
    admin_id = session.get('admin_user_id') or session.get('user_id')
    current_admin = User.query.get(admin_id) or User.query.filter(User.role.in_(['admin', 'super_admin'])).first()
    return render_template('admin/settings.html', settings=settings, current_admin=current_admin)

@admin_bp.route('/update-credentials', methods=['POST'])
@admin_required
def update_credentials():
    admin_id = session.get('admin_user_id') or session.get('user_id')
    admin_user = User.query.get(admin_id) or User.query.filter(User.role.in_(['admin', 'super_admin'])).first()
    
    if not admin_user:
        flash("Admin user account not found.", "danger")
        return redirect(url_for('admin.settings_page'))
    
    current_password = request.form.get('current_password', '').strip()
    new_email = request.form.get('new_email', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()

    if not check_password_hash(admin_user.password, current_password):
        flash("Current password verification failed. Credentials were not updated.", "danger")
        return redirect(url_for('admin.settings_page'))

    if new_password and new_password != confirm_password:
        flash("New password and confirm password do not match.", "warning")
        return redirect(url_for('admin.settings_page'))

    changes = []
    if new_email and new_email != admin_user.email:
        existing = User.query.filter(User.email == new_email, User.id != admin_user.id).first()
        if existing:
            flash("That email address is already in use by another account.", "warning")
            return redirect(url_for('admin.settings_page'))
        admin_user.email = new_email
        session['admin_user_email'] = new_email
        changes.append(f"email to '{new_email}'")

    if new_password:
        admin_user.password = generate_password_hash(new_password)
        changes.append("password")

    if changes:
        db.session.commit()
        log_admin_action("Update Admin Credentials", "AdminUser", admin_user.id, f"Updated admin {', '.join(changes)}")
        flash(f"🎉 Administrator credentials updated successfully! ({', '.join(changes)})", "success")
    else:
        flash("No changes made to administrator credentials.", "info")

    return redirect(url_for('admin.settings_page'))

