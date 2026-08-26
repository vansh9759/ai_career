from database import db
from flask_login import UserMixin
from datetime import datetime
import json

# ---------------- USER TABLE ---------------- #
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), default="student") # student, recruiter, company, university, admin
    is_verified = db.Column(db.Boolean, default=False)
    photo_url = db.Column(db.String(300), default="/static/images/default_avatar.png")
    
    # Career Details
    dream_company = db.Column(db.String(100), default="Google")
    dream_job = db.Column(db.String(100), default="Software Engineer")
    career_goal = db.Column(db.String(200), default="Full Stack AI Engineer")
    college = db.Column(db.String(200), default="Tech University")
    degree = db.Column(db.String(100), default="B.Tech Computer Science")
    
    # Portfolio & Social Handles
    github = db.Column(db.String(300), default="")
    linkedin = db.Column(db.String(300), default="")
    leetcode = db.Column(db.String(300), default="")
    hackerrank = db.Column(db.String(300), default="")
    codeforces = db.Column(db.String(300), default="")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    resumes = db.relationship("Resume", backref="user", lazy=True, cascade="all, delete-orphan")
    employability_scores = db.relationship("EmployabilityScore", backref="user", lazy=True, cascade="all, delete-orphan")
    verified_skills = db.relationship("VerifiedSkill", backref="user", lazy=True, cascade="all, delete-orphan")
    submissions = db.relationship("CodingSubmission", backref="user", lazy=True, cascade="all, delete-orphan")
    mock_interviews = db.relationship("MockInterviewSession", backref="user", lazy=True, cascade="all, delete-orphan")
    applications = db.relationship("JobApplication", backref="user", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.name} - {self.role}>"


# ---------------- RESUME TABLE ---------------- #
class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    ats_score = db.Column(db.Integer, default=70)
    resume_score = db.Column(db.Integer, default=75)
    parsed_data = db.Column(db.Text, default="{}")
    analysis_report = db.Column(db.Text, default="{}")
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


# ---------------- BUILT RESUME TABLE ---------------- #
class BuiltResume(db.Model):
    __tablename__ = "built_resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    template_theme = db.Column(db.String(50), default="modern")
    full_name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(30))
    address = db.Column(db.String(300))
    linkedin = db.Column(db.String(300))
    github = db.Column(db.String(300))
    summary = db.Column(db.Text)
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    projects = db.Column(db.Text)
    experience = db.Column(db.Text)
    certifications = db.Column(db.Text)
    achievements = db.Column(db.Text)
    languages = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- AI EMPLOYABILITY INDEX TABLE ---------------- #
class EmployabilityScore(db.Model):
    __tablename__ = "employability_scores"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_score = db.Column(db.Integer, default=68)
    
    # Sub-scores
    resume_quality = db.Column(db.Integer, default=70)
    ats_score = db.Column(db.Integer, default=65)
    technical_skills = db.Column(db.Integer, default=72)
    verified_skills = db.Column(db.Integer, default=60)
    coding_performance = db.Column(db.Integer, default=75)
    project_quality = db.Column(db.Integer, default=70)
    github_activity = db.Column(db.Integer, default=65)
    interview_performance = db.Column(db.Integer, default=60)
    communication = db.Column(db.Integer, default=70)
    company_match = db.Column(db.Integer, default=68)

    explanation = db.Column(db.Text, default="Your Employability Score is steadily increasing. Complete 2 coding challenges to reach 75.")
    score_delta = db.Column(db.Integer, default=3)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- VERIFIED SKILL PASSPORT ---------------- #
class VerifiedSkill(db.Model):
    __tablename__ = "verified_skills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    proficiency = db.Column(db.String(50), default="Intermediate")
    status = db.Column(db.String(30), default="Verified")
    verification_method = db.Column(db.String(100), default="AI Coding Test & Quiz")
    badge_code = db.Column(db.String(100), unique=True)
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- LEARNING ROADMAP & LMS ---------------- #
class LearningRoadmap(db.Model):
    __tablename__ = "learning_roadmaps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    goal_title = db.Column(db.String(150), default="AI Engineer")
    progress_pct = db.Column(db.Integer, default=45)
    roadmap_nodes_json = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), default="Programming")
    instructor = db.Column(db.String(100), default="CareerOS AI Academy")
    duration = db.Column(db.String(50), default="8 Hours")
    difficulty = db.Column(db.String(50), default="Intermediate")
    description = db.Column(db.Text)
    skills_mapped = db.Column(db.String(200))
    rating = db.Column(db.Float, default=4.9)
    enrolled_count = db.Column(db.Integer, default=1240)


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.String(30), default="15 mins")
    video_url = db.Column(db.String(300), default="https://www.youtube.com/embed/rfscVS0vtbw")
    content_notes = db.Column(db.Text)


# ---------------- PROJECT BLUEPRINT TABLE ---------------- #
class ProjectBlueprint(db.Model):
    __tablename__ = "project_blueprints"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    level = db.Column(db.String(50), default="Advanced")
    category = db.Column(db.String(100), default="AI & Full Stack")
    tech_stack = db.Column(db.String(250), default="Python, Flask, React, PostgreSQL")
    description = db.Column(db.Text)
    architecture = db.Column(db.Text)
    resume_bullets = db.Column(db.Text)


# ---------------- CODING ARENA ---------------- #
class CodingChallenge(db.Model):
    __tablename__ = "coding_challenges"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(30), default="Medium")
    category = db.Column(db.String(100), default="Algorithms")
    company_tag = db.Column(db.String(100), default="Google")
    description = db.Column(db.Text)
    starter_code = db.Column(db.Text)
    test_cases_json = db.Column(db.Text)
    points = db.Column(db.Integer, default=50)


class CodingSubmission(db.Model):
    __tablename__ = "coding_submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("coding_challenges.id"), nullable=False)
    language = db.Column(db.String(30), default="Python")
    code = db.Column(db.Text)
    status = db.Column(db.String(30), default="Passed")
    ai_feedback = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- MOCK INTERVIEW SESSIONS ---------------- #
class MockInterviewSession(db.Model):
    __tablename__ = "mock_interview_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    interview_type = db.Column(db.String(50), default="Technical")
    target_role = db.Column(db.String(100), default="Software Engineer")
    score = db.Column(db.Integer, default=82)
    communication_rating = db.Column(db.Integer, default=85)
    technical_rating = db.Column(db.Integer, default=80)
    feedback_summary = db.Column(db.Text)
    report_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- JOB PORTAL & RECRUITER ---------------- #
class JobPosting(db.Model):
    __tablename__ = "job_postings"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100), default="Remote / Hybrid")
    job_type = db.Column(db.String(50), default="Full-Time")
    salary_range = db.Column(db.String(100), default="$90,000 - $130,000 / yr")
    required_skills = db.Column(db.String(250), default="Python, SQL, Machine Learning")
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class JobApplication(db.Model):
    __tablename__ = "job_applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job_postings.id"), nullable=False)
    ats_match_score = db.Column(db.Integer, default=85)
    status = db.Column(db.String(50), default="Shortlisted")
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- GAMIFICATION & MISSIONS ---------------- #
class GamificationProfile(db.Model):
    __tablename__ = "gamification_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    xp = db.Column(db.Integer, default=1450)
    coins = db.Column(db.Integer, default=320)
    streak_days = db.Column(db.Integer, default=7)
    level = db.Column(db.Integer, default=4)
    badges_json = db.Column(db.Text, default='["7-Day Streak", "Code Ninja", "Verified Python Pro"]')


# ---------------- ADMIN PORTAL & SECURITY MODELS ---------------- #
class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, nullable=True)
    admin_name = db.Column(db.String(100), default="System Admin")
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50), default="General")
    target_id = db.Column(db.String(100), default="")
    ip_address = db.Column(db.String(45), default="127.0.0.1")
    details = db.Column(db.Text, default="")
    result = db.Column(db.String(30), default="Success")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class SystemNotification(db.Model):
    __tablename__ = "system_notifications"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), default="info") # info, success, warning, announcement
    target_audience = db.Column(db.String(30), default="all") # all, selected, premium, free
    scheduled_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default="Sent") # Draft, Scheduled, Sent


class CareerPath(db.Model):
    __tablename__ = "career_paths"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    required_skills = db.Column(db.String(300), default="Python, SQL, Algorithms")
    recommended_skills = db.Column(db.String(300), default="System Design, Docker")
    salary_range = db.Column(db.String(100), default="$100,000 - $160,000")
    difficulty = db.Column(db.String(50), default="Intermediate")
    experience_level = db.Column(db.String(50), default="0-3 Years")
    related_jobs = db.Column(db.String(250), default="Backend Engineer, AI Engineer")
    learning_resources = db.Column(db.Text, default="Python Masterclass, SQL Deep Dive")
    status = db.Column(db.String(30), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SkillMaster(db.Model):
    __tablename__ = "skill_masters"

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100), default="Programming Languages")
    popularity_score = db.Column(db.Integer, default=95)
    description = db.Column(db.Text)
    related_careers = db.Column(db.String(250), default="Full Stack Engineer, Data Scientist")
    status = db.Column(db.String(30), default="Active")


class SubscriptionRecord(db.Model):
    __tablename__ = "subscription_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    plan_name = db.Column(db.String(50), default="Pro Candidate") # Free, Pro Candidate, Enterprise
    status = db.Column(db.String(30), default="Active") # Active, Cancelled, Expired
    mrr_amount = db.Column(db.Float, default=19.0)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)


class PaymentTransaction(db.Model):
    __tablename__ = "payment_transactions"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, default=19.0)
    plan_name = db.Column(db.String(50), default="Pro Candidate")
    payment_method = db.Column(db.String(50), default="Stripe Credit Card")
    status = db.Column(db.String(30), default="Successful") # Successful, Pending, Failed, Refunded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CMSContent(db.Model):
    __tablename__ = "cms_content"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content_type = db.Column(db.String(50), default="guide") # guide, blog, faq, question, roadmap
    content_body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), default="General")
    tags = db.Column(db.String(200), default="Career, AI")
    is_published = db.Column(db.Boolean, default=True)
    author = db.Column(db.String(100), default="CareerOS Team")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class AdminSetting(db.Model):
    __tablename__ = "admin_settings"

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    category = db.Column(db.String(50), default="general") # general, security, ai, email, maintenance
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class AIUsageLog(db.Model):
    __tablename__ = "ai_usage_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    feature_name = db.Column(db.String(100), default="Resume Analyzer")
    tokens_used = db.Column(db.Integer, default=450)
    response_time_ms = db.Column(db.Integer, default=320)
    status_code = db.Column(db.Integer, default=200)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)