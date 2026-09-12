from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import User
from database import db
from services.career_twin import AICareerTwinEngine
from services.scoring import DynamicScoringEngine

career_twin_bp = Blueprint('career_twin', __name__)

@career_twin_bp.route('/')
@career_twin_bp.route('/twin')
def index():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to access your AI Career Twin.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    scoring_data = DynamicScoringEngine.update_user_score(user_id)
    twin_res = AICareerTwinEngine.get_or_create_twin(user_id)
    projections = AICareerTwinEngine.get_projections(user_id)
    plan = AICareerTwinEngine.get_daily_plan(user_id)

    return render_template(
        'career_twin/index.html',
        user=user,
        scoring_data=scoring_data,
        twin=twin_res["twin"],
        snapshot=twin_res["snapshot"],
        projections=projections,
        plan=plan
    )

@career_twin_bp.route('/ask', methods=['POST'])
def ask():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    question = data.get('question', '').strip()
    if not question:
        return jsonify({"error": "Please enter a question for your Career Twin."}), 400

    response_text = AICareerTwinEngine.answer_twin_query(user_id, question)
    return jsonify({
        "success": True,
        "question": question,
        "answer": response_text
    })

@career_twin_bp.route('/report/export')
def export_report():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to export your career report.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    scoring_data = DynamicScoringEngine.update_user_score(user_id)
    twin_res = AICareerTwinEngine.get_or_create_twin(user_id)
    projections = AICareerTwinEngine.get_projections(user_id)
    plan = AICareerTwinEngine.get_daily_plan(user_id)

    return render_template(
        'career_twin/report_pdf.html',
        user=user,
        scoring_data=scoring_data,
        twin=twin_res["twin"],
        snapshot=twin_res["snapshot"],
        projections=projections,
        plan=plan
    )
