import math
import json
from database import db
from models import (
    User, EmployabilityScore, GamificationProfile, VerifiedSkill,
    CodingSubmission, Resume, MockInterviewSession, JobApplication
)
from datetime import datetime, timezone

class DynamicScoringEngine:
    """
    Centralized Unified Scoring & Level Engine for CareerOS AI.
    Calculates exact real candidate employability index, sub-scores, 
    and XP level progression directly from database records.
    """

    @staticmethod
    def calculate_user_level(xp):
        """
        Calculates user level and exact progress toward next level.
        Formula: Level = floor(sqrt(XP / 100)) + 1
        """
        xp = max(0, xp or 0)
        level = int(math.sqrt(xp / 100.0)) + 1
        
        # Calculate bounds for current level
        current_level_min_xp = (level - 1) ** 2 * 100
        next_level_min_xp = level ** 2 * 100
        
        xp_in_current_level = xp - current_level_min_xp
        xp_needed_for_level = next_level_min_xp - current_level_min_xp
        
        progress_pct = int((xp_in_current_level / xp_needed_for_level) * 100) if xp_needed_for_level > 0 else 100
        progress_pct = max(0, min(100, progress_pct))

        return {
            "level": level,
            "xp": xp,
            "current_level_min_xp": current_level_min_xp,
            "next_level_min_xp": next_level_min_xp,
            "xp_in_level": xp_in_current_level,
            "xp_needed": xp_needed_for_level,
            "progress_pct": progress_pct
        }

    @staticmethod
    def update_user_score(user_id):
        """
        Re-calculates and persists unified EmployabilityScore & GamificationProfile for a candidate.
        """
        user = db.session.get(User, user_id)
        if not user:
            return None

        # 1. Resume Quality & ATS Score
        latest_resume = Resume.query.filter_by(user_id=user_id).order_by(Resume.upload_date.desc()).first()
        resume_quality = latest_resume.resume_score if latest_resume else 65
        ats_score = latest_resume.ats_score if latest_resume else 60

        # 2. Verified Skills Score
        verified_count = VerifiedSkill.query.filter_by(user_id=user_id, status="Verified").count()
        verified_skills_score = min(98, max(40, 50 + (verified_count * 15)))

        # 3. Coding Performance
        passed_submissions = CodingSubmission.query.filter_by(user_id=user_id, status="Passed").count()
        total_submissions = CodingSubmission.query.filter_by(user_id=user_id).count()
        pass_ratio = (passed_submissions / total_submissions) if total_submissions > 0 else 0.5
        coding_performance = min(99, max(45, int(50 + (passed_submissions * 10) + (pass_ratio * 20))))

        # 4. Mock Interview Performance
        latest_interview = MockInterviewSession.query.filter_by(user_id=user_id).order_by(MockInterviewSession.created_at.desc()).first()
        interview_score = latest_interview.score if latest_interview else 65
        communication_score = latest_interview.communication_rating if latest_interview else 70

        # 5. Project Quality & Applications
        apps_count = JobApplication.query.filter_by(user_id=user_id).count()
        project_quality = min(95, max(50, 60 + (apps_count * 8)))

        # 6. Centralized Overall Employability Index Formula
        # Weights: Resume (15%), ATS (15%), Coding (25%), Skills (20%), Projects (15%), Interviews (10%)
        total_score = int(
            (resume_quality * 0.15) +
            (ats_score * 0.15) +
            (coding_performance * 0.25) +
            (verified_skills_score * 0.20) +
            (project_quality * 0.15) +
            (interview_score * 0.10)
        )
        total_score = max(35, min(99, total_score))

        # Update or Create EmployabilityScore record
        emp = EmployabilityScore.query.filter_by(user_id=user_id).first()
        if not emp:
            emp = EmployabilityScore(user_id=user_id)
            db.session.add(emp)

        old_score = emp.total_score or 65
        old_coding = emp.coding_performance or 50
        old_skills = emp.verified_skills or 50
        old_interview = emp.interview_performance or 65
        old_resume = emp.resume_quality or 65

        dsa_delta = coding_performance - old_coding
        skills_delta = verified_skills_score - old_skills
        interview_delta = interview_score - old_interview
        resume_delta = resume_quality - old_resume

        reasons = []
        if dsa_delta != 0:
            reasons.append(f"DSA {'+' if dsa_delta > 0 else ''}{dsa_delta} ({passed_submissions} solved)")
        if skills_delta != 0:
            reasons.append(f"Skills {'+' if skills_delta > 0 else ''}{skills_delta} ({verified_count} verified)")
        if interview_delta != 0:
            reasons.append(f"Interview {'+' if interview_delta > 0 else ''}{interview_delta}")
        if resume_delta != 0:
            reasons.append(f"Resume {'+' if resume_delta > 0 else ''}{resume_delta}")

        score_delta = total_score - old_score
        explanation_str = f"Score {total_score} ({'+' if score_delta >= 0 else ''}{score_delta} pts): " + (", ".join(reasons) if reasons else "Score updated based on candidate assessment activity.")

        emp.total_score = total_score
        emp.resume_quality = resume_quality
        emp.ats_score = ats_score
        emp.verified_skills = verified_skills_score
        emp.coding_performance = coding_performance
        emp.project_quality = project_quality
        emp.interview_performance = interview_score
        emp.communication = communication_score
        emp.score_delta = score_delta
        emp.explanation = explanation_str
        emp.breakdown_json = json.dumps({
            "dsa_delta": dsa_delta,
            "skills_delta": skills_delta,
            "interview_delta": interview_delta,
            "resume_delta": resume_delta,
            "reasons": reasons
        })
        emp.last_updated = datetime.now(timezone.utc).replace(tzinfo=None)

        # Update Gamification Profile Level
        gam = GamificationProfile.query.filter_by(user_id=user_id).first()
        if not gam:
            gam = GamificationProfile(user_id=user_id, xp=500, coins=100, level=2)
            db.session.add(gam)
        
        level_info = DynamicScoringEngine.calculate_user_level(gam.xp)
        gam.level = level_info["level"]

        db.session.commit()
        return {
            "total_score": total_score,
            "level_info": level_info,
            "score_delta": score_delta,
            "explanation": explanation_str,
            "breakdown": {
                "dsa_delta": dsa_delta,
                "skills_delta": skills_delta,
                "interview_delta": interview_delta,
                "resume_delta": resume_delta
            },
            "employability_record": emp
        }
