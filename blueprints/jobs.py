from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from database import db
from models import JobPosting, JobApplication, User

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/portal')
def portal():
    jobs = JobPosting.query.all()
    if not jobs:
        j1 = JobPosting(company_name="Google", title="Associate Software Engineer", location="Mountain View, CA / Hybrid", salary_range="$120,000 - $150,000", required_skills="Python, SQL, Algorithms", description="Join Google Core Engineering to build scalable cloud infra.")
        j2 = JobPosting(company_name="Microsoft", title="AI / ML Engineer Intern", location="Redmond, WA / Remote", salary_range="$50 / hr", required_skills="PyTorch, Python, Machine Learning", description="Work on cutting-edge Copilot & OpenAI models.")
        j3 = JobPosting(company_name="Amazon", title="Frontend Developer", location="Seattle, WA", salary_range="$110,000 - $140,000", required_skills="React, JavaScript, CSS", description="Build high-concurrency retail web experiences.")
        db.session.add_all([j1, j2, j3])
        db.session.commit()
        jobs = JobPosting.query.all()

    return render_template('jobs/portal.html', jobs=jobs)

@jobs_bp.route('/apply/<int:job_id>', methods=['POST'])
def apply(job_id):
    user_id = session.get('user_id', 1)
    new_app = JobApplication(user_id=user_id, job_id=job_id, ats_match_score=88, status="Shortlisted")
    db.session.add(new_app)
    db.session.commit()
    flash('Application submitted! AI has matched your profile as Top 10% Candidate.', 'success')
    return redirect(url_for('jobs.portal'))
