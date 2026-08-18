from flask import Blueprint, render_template

university_bp = Blueprint('university', __name__)

@university_bp.route('/dashboard')
def dashboard():
    metrics = {
        "total_students": 1420,
        "placement_rate": "89.4%",
        "avg_employability_index": 76,
        "avg_ats_score": 78,
        "top_recruiting_partners": ["Google", "Microsoft", "Amazon", "Infosys", "TCS"],
        "department_stats": [
            {"dept": "Computer Science & Engineering", "students": 520, "placed": "94%", "avg_index": 82},
            {"dept": "Information Technology", "students": 380, "placed": "91%", "avg_index": 79},
            {"dept": "Data Science & AI", "students": 240, "placed": "88%", "avg_index": 77},
            {"dept": "Electronics & Communication", "students": 280, "placed": "82%", "avg_index": 71}
        ]
    }
    return render_template('university/dashboard.html', metrics=metrics)
