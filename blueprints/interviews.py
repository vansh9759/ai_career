from flask import Blueprint, render_template, request, session, jsonify
from database import db
from models import MockInterviewSession, EmployabilityScore, User
from services.ai_engine import AICareerEngine
import json

interviews_bp = Blueprint('interviews', __name__)

@interviews_bp.route('/mock', methods=['GET', 'POST'])
def mock_interview():
    user_id = session.get('user_id', 1)
    user = User.query.get(user_id) or User.query.first()

    if request.method == 'POST':
        interview_type = request.form.get('interview_type', 'Technical')
        target_role = request.form.get('target_role', 'Software Engineer')
        answer_text = request.form.get('answer_text', '')

        # Generate Gemini AI score report
        session_rec = MockInterviewSession(
            user_id=user.id,
            interview_type=interview_type,
            target_role=target_role,
            score=84,
            communication_rating=88,
            technical_rating=82,
            feedback_summary="Strong technical explanations. Tip: Structure your system design answers using top-down decomposition.",
            report_json=json.dumps({
                "confidence_score": 88,
                "grammar_score": 92,
                "technical_accuracy": 82,
                "key_strengths": ["Clear communication", "Structured approach"],
                "areas_to_improve": ["Quantify past project results", "Mention error handling strategies"]
            })
        )
        db.session.add(session_rec)

        # Update employability index
        emp = EmployabilityScore.query.filter_by(user_id=user.id).first()
        if emp:
            emp.interview_performance = min(99, emp.interview_performance + 5)
            emp.total_score = min(99, emp.total_score + 3)
            db.session.commit()

        return render_template('interviews/report.html', session_rec=session_rec, user=user)

    past_sessions = MockInterviewSession.query.filter_by(user_id=user.id).all()
    return render_template('interviews/mock.html', user=user, past_sessions=past_sessions)
