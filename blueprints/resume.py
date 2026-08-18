from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import db
from models import User, Resume, BuiltResume, EmployabilityScore
from services.ai_engine import AICareerEngine
from resume_parser import extract_text_from_filepath
from werkzeug.utils import secure_filename
import os
import json

resume_bp = Blueprint('resume', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@resume_bp.route('/builder', methods=['GET', 'POST'])
def builder():
    user_id = session.get('user_id', 1)
    built_resume = BuiltResume.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        if not built_resume:
            built_resume = BuiltResume(user_id=user_id)
            db.session.add(built_resume)
        
        built_resume.full_name = request.form.get('full_name')
        built_resume.email = request.form.get('email')
        built_resume.phone = request.form.get('phone')
        built_resume.linkedin = request.form.get('linkedin')
        built_resume.github = request.form.get('github')
        built_resume.summary = request.form.get('summary')
        built_resume.education = request.form.get('education')
        built_resume.skills = request.form.get('skills')
        built_resume.projects = request.form.get('projects')
        built_resume.experience = request.form.get('experience')
        built_resume.template_theme = request.form.get('template_theme', 'modern')

        db.session.commit()

        # Update employability score
        emp = EmployabilityScore.query.filter_by(user_id=user_id).first()
        if emp:
            emp.resume_quality = min(98, emp.resume_quality + 5)
            emp.last_updated = db.func.current_timestamp()
            db.session.commit()

        flash('Resume saved and Employability Score updated!', 'success')
        return redirect(url_for('resume.builder'))

    return render_template('resume/builder.html', resume=built_resume)


@resume_bp.route('/analyzer', methods=['GET', 'POST'])
def analyzer():
    report = None
    if request.method == 'POST':
        resume_text = request.form.get('resume_text', '').strip()
        
        # Process File Upload (PDF, DOCX, TXT)
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                # Extract text using multi-library fallback parser
                extracted = extract_text_from_filepath(file_path)
                if extracted:
                    resume_text = extracted

        if not resume_text or len(resume_text) < 15:
            flash('Please select a valid PDF/DOCX resume file or paste text to analyze.', 'warning')
        else:
            report = AICareerEngine.analyze_resume(resume_text)
            
            # Save Resume & update Employability Score in DB
            user_id = session.get('user_id', 1)
            if 'error' not in report:
                new_resume = Resume(
                    filename="uploaded_resume.pdf",
                    ats_score=report.get('ats_score', 70),
                    resume_score=report.get('resume_score', 75),
                    parsed_data=json.dumps({"word_count": report.get('word_count', 0)}),
                    analysis_report=json.dumps(report),
                    user_id=user_id
                )
                db.session.add(new_resume)

                # Update live Employability Score
                emp = EmployabilityScore.query.filter_by(user_id=user_id).first()
                if emp:
                    emp.ats_score = report.get('ats_score', 75)
                    emp.resume_quality = report.get('resume_score', 78)
                    emp.total_score = min(99, int((emp.resume_quality * 0.15) + (emp.ats_score * 0.15) + (emp.coding_performance * 0.25) + (emp.verified_skills * 0.20) + (emp.project_quality * 0.15) + (emp.interview_performance * 0.10)))
                    db.session.commit()

                flash(f"Resume analysis complete! ATS Score: {report.get('ats_score')}/100.", 'success')

    return render_template('resume/analyzer.html', report=report)


@resume_bp.route('/match-jd', methods=['GET', 'POST'])
def match_jd():
    match_result = None
    if request.method == 'POST':
        resume_text = request.form.get('resume_text', '').strip()
        job_description = request.form.get('job_description', '').strip()

        if not resume_text or not job_description:
            flash('Please paste both your resume text and target job description.', 'warning')
        else:
            match_result = AICareerEngine.match_resume_vs_jd(resume_text, job_description)

    return render_template('resume/match_jd.html', match_result=match_result)
