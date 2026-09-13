from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import User, GitHubProfile
from database import db
from services.github_engine import GitHubEngineeringEngine
from services.scoring import DynamicScoringEngine

github_bp = Blueprint('github', __name__)

@github_bp.route('/', methods=['GET', 'POST'])
def index():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to evaluate your GitHub Engineering Score.", "warning")
        return redirect(url_for('auth.login'))

    user = db.session.get(User, user_id)
    analysis = None
    username = user.github or "alexrivera"

    if request.method == 'POST':
        input_handle = request.form.get('github_handle', '').strip()
        if input_handle:
            username = input_handle
            user.github = input_handle
            db.session.commit()

    analysis = GitHubEngineeringEngine.evaluate_profile(username)

    # Save to GitHubProfile model
    gh_profile = GitHubProfile.query.filter_by(user_id=user_id).first()
    if not gh_profile:
        gh_profile = GitHubProfile(
            user_id=user_id,
            username=analysis['username'],
            repo_count=analysis['repo_count'],
            commit_count=analysis['total_commits'],
            engineering_score=analysis['github_engineering_score']
        )
        db.session.add(gh_profile)
    else:
        gh_profile.username = analysis['username']
        gh_profile.repo_count = analysis['repo_count']
        gh_profile.commit_count = analysis['total_commits']
        gh_profile.engineering_score = analysis['github_engineering_score']
    
    db.session.commit()
    DynamicScoringEngine.update_user_score(user_id)

    return render_template('github/index.html', user=user, analysis=analysis)
