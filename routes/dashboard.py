import json
from flask import Blueprint, render_template, session, redirect, url_for
from models.user import User
from models.personality import PersonalityProfile
from models.relationship import Relationship
from models.compatibility import CompatibilityResult
from models.chat_analysis import ChatAnalysis
from models.astrology import AstrologyReading
from models.relationship_plan import RelationshipPlan, DailyTask
from models.assessment import AssessmentSnapshot
from services.assessment_service import AssessmentService

dashboard_bp = Blueprint("dashboard", __name__)

def _json(value, default):
    try:
        return json.loads(value or "")
    except Exception:
        return default

@dashboard_bp.route("/dashboard")
def index():
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login"))
    user = User.query.get(uid)
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    personality = PersonalityProfile.query.filter_by(user_id=uid).first()
    relationship = Relationship.query.filter_by(user_id=uid, status="active").order_by(Relationship.id.desc()).first()
    compatibility = CompatibilityResult.query.filter_by(relationship_id=relationship.id).order_by(CompatibilityResult.id.desc()).first() if relationship else None
    chats = ChatAnalysis.query.filter_by(user_id=uid).order_by(ChatAnalysis.created_at.desc()).all()
    chat = chats[0] if chats else None
    astrology = AstrologyReading.query.filter_by(user_id=uid).order_by(AstrologyReading.id.desc()).first()

    assessment = AssessmentService.calculate(uid, save=False)
    assessment_history = AssessmentSnapshot.query.filter_by(user_id=uid).order_by(AssessmentSnapshot.created_at.desc()).limit(10).all()
    plan = AssessmentService.ensure_plan(assessment) if assessment else None
    tasks = DailyTask.query.filter_by(plan_id=plan.id).order_by(DailyTask.day_number.asc()).all() if plan else []
    completed_tasks = sum(1 for task in tasks if task.completed)

    return render_template(
        "dashboard.html",
        user=user,
        personality=personality,
        relationship=relationship,
        compatibility=compatibility,
        chat=chat,
        chats=chats,
        astrology=astrology,
        assessment=assessment,
        assessment_history=assessment_history,
        plan=plan,
        tasks=tasks,
        completed_tasks=completed_tasks,
        chat_result=_json(chat.ai_analysis_json, {}) if chat else {},
    )
