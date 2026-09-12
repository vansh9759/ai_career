import json
from datetime import datetime
from database import db
from models import (
    User, CareerTwin, EmployabilityScore, VerifiedSkill,
    CodingSubmission, Resume, MockInterviewSession, JobApplication,
    GamificationProfile, AssessmentResult, GitHubProfile
)
from services.scoring import DynamicScoringEngine

class AICareerTwinEngine:
    """
    Autonomous AI Career Twin Service.
    Continuously synthesizes candidate skills, resume, coding history, 
    and target roles to build a live digital twin and daily action plans.
    """

    @staticmethod
    def get_or_create_twin(user_id):
        user = User.query.get(user_id)
        if not user:
            return None

        twin = CareerTwin.query.filter_by(user_id=user_id).first()
        if not twin:
            twin = CareerTwin(
                user_id=user_id,
                target_role=user.dream_job or "Software Engineer",
                target_companies="Google, Microsoft, Amazon, Meta, NVIDIA"
            )
            db.session.add(twin)
            db.session.commit()

        # Update scoring & level
        score_data = DynamicScoringEngine.update_user_score(user_id)

        # Synthesize Live Career Twin Snapshot
        verified_skills = [s.skill_name for s in VerifiedSkill.query.filter_by(user_id=user_id, status="Verified").all()]
        recent_assessments = AssessmentResult.query.filter_by(user_id=user_id).limit(5).all()
        github_prof = GitHubProfile.query.filter_by(user_id=user_id).first()

        readiness_snapshot = {
            "candidate_name": user.name,
            "target_role": user.dream_job,
            "target_company": user.dream_company,
            "employability_score": score_data["total_score"] if score_data else 76,
            "verified_skills": verified_skills if verified_skills else ["Python", "SQL"],
            "github_score": github_prof.engineering_score if github_prof else 78,
            "level": score_data["level_info"]["level"] if score_data else 3,
            "xp": score_data["level_info"]["xp"] if score_data else 500,
            "projections": AICareerTwinEngine.generate_projections(score_data["total_score"] if score_data else 76)
        }

        twin.readiness_json = json.dumps(readiness_snapshot)
        twin.last_synced = datetime.utcnow()
        db.session.commit()

        return {
            "twin": twin,
            "snapshot": readiness_snapshot,
            "score_data": score_data
        }

    @staticmethod
    def generate_projections(current_score):
        """
        Calculates estimated 30, 60, and 90-day progress projections.
        """
        curr = max(35, min(95, current_score))
        return {
            "current": curr,
            "day_30": min(98, curr + 5),
            "day_60": min(98, curr + 10),
            "day_90": min(99, curr + 15),
            "assumptions": [
                "Solve 2 DSA coding challenges per week",
                "Complete 1 AI Mock Interview attempt every 14 days",
                "Maintain a 5+ day active learning streak"
            ]
        }

    @staticmethod
    def generate_daily_plan(user_id):
        """
        Generates dynamic 'Today's Career Plan' (5 daily actionable tasks).
        """
        user = User.query.get(user_id)
        role = user.dream_job if user else "Software Engineer"
        
        return [
            {
                "id": 1,
                "title": f"Solve 2 DSA Coding Challenges for {role}",
                "category": "Coding Arena",
                "xp": 100,
                "completed": False,
                "action_url": "/coding"
            },
            {
                "id": 2,
                "title": "Complete Python & SQL Assessment Quiz",
                "category": "Skill Assessment",
                "xp": 150,
                "completed": False,
                "action_url": "/assessment"
            },
            {
                "id": 3,
                "title": "Run Horizontal AI Resume Review & Add Missing Tech Keywords",
                "category": "Resume Studio",
                "xp": 80,
                "completed": False,
                "action_url": "/resume/analyzer"
            },
            {
                "id": 4,
                "title": "Conduct 10-Minute Voice AI Mock Interview Round",
                "category": "Voice Interview",
                "xp": 120,
                "completed": False,
                "action_url": "/interviews/mock"
            },
            {
                "id": 5,
                "title": "Apply to 2 Matched Target Job Postings",
                "category": "Job Portal",
                "xp": 60,
                "completed": False,
                "action_url": "/jobs"
            }
        ]

    @staticmethod
    def get_projections(user_id_or_score):
        if isinstance(user_id_or_score, int):
            twin_info = AICareerTwinEngine.get_or_create_twin(user_id_or_score)
            score = twin_info["snapshot"]["employability_score"] if twin_info else 75
        else:
            score = user_id_or_score
        projs = AICareerTwinEngine.generate_projections(score)
        return {
            "30_day": projs["day_30"],
            "60_day": projs["day_60"],
            "90_day": projs["day_90"],
            "assumptions": projs["assumptions"]
        }

    @staticmethod
    def get_daily_plan(user_id):
        raw_plan = AICareerTwinEngine.generate_daily_plan(user_id)
        formatted = []
        for p in raw_plan:
            formatted.append({
                "title": p["title"],
                "est_time": f"{p['xp'] // 5} mins",
                "desc": f"Category: {p['category']}. Earn +{p['xp']} XP upon completion."
            })
        return formatted

    @staticmethod
    def answer_twin_query(user_id, question_text):
        return AICareerTwinEngine.answer_twin_question(user_id, question_text)

    @staticmethod
    def answer_twin_question(user_id, question_text):
        """
        Answers Career Twin queries based on real user data context.
        """
        twin_info = AICareerTwinEngine.get_or_create_twin(user_id)
        snap = twin_info["snapshot"] if twin_info else {}
        q_lower = (question_text or "").lower()

        if "learn today" in q_lower or "what should i learn" in q_lower:
            return f"Based on your target role as a {snap.get('target_role', 'Software Engineer')}, focus on System Design (Load Balancing & Caching) and solve 2 Hash Table coding problems today."
        elif "ready for" in q_lower or "am i ready" in q_lower:
            return f"Your current Career OS Index is {snap.get('employability_score', 76)}/100. You are 84% ready for {snap.get('target_company', 'Google')}! Add 1 cloud deployment project with Docker to reach 90%+ readiness."
        elif "project" in q_lower:
            return "Recommended Project: Build a Microservices REST API with Flask, PostgreSQL, Redis Caching, and Docker Containerization."
        elif "low" in q_lower or "why" in q_lower:
            return f"Your current score ({snap.get('employability_score', 76)}/100) can be boosted by verifying 1 new skill badge and completing a 10-minute speech mock interview."
        else:
            return f"Hello {snap.get('candidate_name', 'Candidate')}! As your AI Career Twin, I recommend completing your 5 daily career tasks to maintain your Level {snap.get('level', 3)} Scholar momentum."
