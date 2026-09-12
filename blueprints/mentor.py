from flask import Blueprint, render_template, request, session, jsonify
from models import User
from services.ai_engine import query_ai_engine
from services.career_twin import AICareerTwinEngine

mentor_bp = Blueprint('mentor', __name__)

PERSONA_PROMPTS = {
    "Career Advisor": "You are an executive Tech Career Advisor. Provide strategic career guidance, resume positioning advice, and salary negotiation insights.",
    "Interview Coach": "You are a Principal Technical Recruiter & Interview Coach. Help candidates structure answers using the STAR method (Situation, Task, Action, Result).",
    "Coding Mentor": "You are a Senior Staff Software Engineer and Competitive Programmer. Explain DSA algorithms, time complexity, and code optimization clearly.",
    "Study Coach": "You are a Tech Learning Productivity Coach. Design focused daily study plans, discipline routines, and roadmap milestones."
}

@mentor_bp.route('/')
@mentor_bp.route('/chat')
def chat():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    return render_template('mentor/chat.html', user=user, personas=PERSONA_PROMPTS)

@mentor_bp.route('/api/ask', methods=['POST'])
def api_ask():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    persona = data.get('persona', 'Career Advisor')
    
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    user_name = user.name if user else 'Candidate'

    sys_instruction = PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["Career Advisor"])
    
    twin_context = ""
    if user_id:
        twin = AICareerTwinEngine.get_or_create_twin(user_id)
        twin_context = f"\nCandidate Profile: Goal='{user.career_goal or 'Software Engineer'}', Target Company='{user.dream_company or 'Tech Co'}', Employability Score={twin.employability_score}."

    full_prompt = f"Candidate ({user_name}) asks: '{message}'{twin_context}"
    ai_res = query_ai_engine(full_prompt, system_instruction=sys_instruction)
    
    return jsonify({
        "response": ai_res.get('text', 'Stay persistent and keep coding!'),
        "persona": persona,
        "badge": ai_res.get('badge', '🤖 CareerOS AI Engine')
    })
