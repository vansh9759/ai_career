from flask import Flask, render_template, redirect, url_for, session
from config import Config
from database import db
from werkzeug.security import generate_password_hash
import os

# Import Models
from models import User, EmployabilityScore, VerifiedSkill, Course, CodingChallenge, JobPosting, GamificationProfile

# Import Blueprints
from blueprints.auth import auth_bp
from blueprints.student import student_bp
from blueprints.resume import resume_bp
from blueprints.skills import skills_bp
from blueprints.learning import learning_bp
from blueprints.coding import coding_bp
from blueprints.projects import projects_bp
from blueprints.interviews import interviews_bp
from blueprints.mentor import mentor_bp
from blueprints.jobs import jobs_bp
from blueprints.recruiter import recruiter_bp
from blueprints.university import university_bp
from blueprints.portfolio import portfolio_bp
from blueprints.admin import admin_bp
from blueprints.admin_api import admin_api_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database
db.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(resume_bp, url_prefix='/resume')
app.register_blueprint(skills_bp, url_prefix='/skills')
app.register_blueprint(learning_bp, url_prefix='/learning')
app.register_blueprint(coding_bp, url_prefix='/coding')
app.register_blueprint(projects_bp, url_prefix='/projects')
app.register_blueprint(interviews_bp, url_prefix='/interviews')
app.register_blueprint(mentor_bp, url_prefix='/mentor')
app.register_blueprint(jobs_bp, url_prefix='/jobs')
app.register_blueprint(recruiter_bp, url_prefix='/recruiter')
app.register_blueprint(university_bp, url_prefix='/university')
app.register_blueprint(portfolio_bp, url_prefix='/portfolio')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(admin_api_bp, url_prefix='/api/admin')


# Global Context Processors
@app.context_processor
def inject_global_vars():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user)


# Home Landing Page Route
@app.route('/')
def home():
    return render_template('index.html')


# Pricing & SaaS Subscription Gateway Routes
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/upgrade-plan', methods=['POST'])
def upgrade_plan():
    from flask import flash, request
    plan = request.form.get('plan', 'Pro Candidate')
    flash(f"🎉 Stripe Checkout Simulation Success! You are now subscribed to the {plan} tier.", "success")
    return redirect(url_for('student.dashboard'))


# Backward compatibility redirects
@app.route('/dashboard')
def dashboard_redirect():
    return redirect(url_for('student.dashboard'))

@app.route('/login')
def login_redirect():
    return redirect(url_for('auth.login'))

@app.route('/register')
def register_redirect():
    return redirect(url_for('auth.register'))


# Database Setup & Schema Migration Helper
with app.app_context():
    try:
        db.create_all()
        
        # Seed Default Super Admin
        admin_user = User.query.filter_by(email="admin@careeros.ai").first()
        if not admin_user:
            admin_user = User(
                name="Super Administrator",
                email="admin@careeros.ai",
                password=generate_password_hash(os.environ.get("ADMIN_PASSWORD", "Admin@12345")),
                role="super_admin",
                dream_company="CareerOS AI",
                dream_job="Chief Technology Officer"
            )
            db.session.add(admin_user)
            db.session.commit()

        # Seed Default Student User if empty
        if User.query.filter_by(email="alex@careeros.ai").count() == 0:
            demo_user = User(
                name="Alex Rivera",
                email="alex@careeros.ai",
                password=generate_password_hash("password123"),
                role="student",
                dream_company="Google",
                dream_job="Software Engineer",
                career_goal="Full Stack AI Engineer",
                college="Stanford University",
                degree="B.S. Computer Science",
                github="github.com/alexrivera",
                linkedin="linkedin.com/in/alexrivera",
                leetcode="leetcode.com/alexrivera"
            )
            db.session.add(demo_user)
            db.session.commit()

            emp = EmployabilityScore(user_id=demo_user.id, total_score=78)
            gam = GamificationProfile(user_id=demo_user.id, xp=2400, coins=450, streak_days=12, level=5)
            sk1 = VerifiedSkill(user_id=demo_user.id, skill_name="Python", proficiency="Verified Expert", status="Verified", badge_code="VERIFIED-PY-88A91")
            sk2 = VerifiedSkill(user_id=demo_user.id, skill_name="SQL", proficiency="Verified Specialist", status="Verified", badge_code="VERIFIED-SQL-91F22")
            sk3 = VerifiedSkill(user_id=demo_user.id, skill_name="Machine Learning", proficiency="Verified Intermediate", status="Verified", badge_code="VERIFIED-ML-44C10")
            db.session.add_all([emp, gam, sk1, sk2, sk3])
            db.session.commit()

        # Seed Sample Admin Models Data if empty
        from models import SkillMaster, CareerPath, SystemNotification, CMSContent, PaymentTransaction, SubscriptionRecord
        if SkillMaster.query.count() == 0:
            sk_list = [
                SkillMaster(skill_name="Python 3", category="Programming", popularity_score=98, description="Primary language for AI/ML and web backend development."),
                SkillMaster(skill_name="SQL & Relational DBs", category="Database", popularity_score=95, description="Essential for data analytics and backend query optimization."),
                SkillMaster(skill_name="Machine Learning & PyTorch", category="AI & ML", popularity_score=92, description="Model training, inference, and fine-tuning."),
                SkillMaster(skill_name="React & TypeScript", category="Frontend", popularity_score=90, description="Modern web applications and interactive UI design.")
            ]
            db.session.add_all(sk_list)

        if CareerPath.query.count() == 0:
            cp_list = [
                CareerPath(title="Full Stack AI Systems Engineer", description="Architect end-to-end AI applications using Flask, React, and LLM APIs.", salary_range="$120,000 - $175,000", difficulty="Intermediate"),
                CareerPath(title="AI & Machine Learning Scientist", description="Design deep learning models, PyTorch pipelines, and predictive algorithms.", salary_range="$140,000 - $210,000", difficulty="Advanced")
            ]
            db.session.add_all(cp_list)

        if SystemNotification.query.count() == 0:
            n1 = SystemNotification(title="Welcome to CareerOS AI 2.0", message="All candidate skill passports and AI resume engines are fully updated.", type="announcement", target_audience="all")
            db.session.add(n1)

        if CMSContent.query.count() == 0:
            c1 = CMSContent(title="How to Crack Google Technical Interviews in 2026", slug="crack-google-interviews-2026", content_body="Comprehensive guide to Data Structures, System Design, and Speech Analytics.", content_type="guide")
            db.session.add(c1)

        db.session.commit()
    except Exception as db_err:
        print(">>> DB Init Warning:", db_err)

if __name__ == '__main__':
    print(">>> CareerOS AI Platform Server Starting... <<<")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)