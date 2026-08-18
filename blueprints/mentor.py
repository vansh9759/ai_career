from flask import Blueprint, render_template, request, session, jsonify
from services.ai_engine import AICareerEngine

mentor_bp = Blueprint('mentor', __name__)

@mentor_bp.route('/chat')
def chat():
    return render_template('mentor/chat.html')

@mentor_bp.route('/api/ask', methods=['POST'])
def api_ask():
    data = request.get_json() or {}
    message = data.get('message', '')
    user_context = session.get('user_name', 'Student')
    response_text = AICareerEngine.ask_ai_mentor(message, user_context)
    return jsonify({"response": response_text})
