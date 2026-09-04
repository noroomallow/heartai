from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from models.compatibility import CompatibilityResult
from models.chat_analysis import ChatAnalysis
from models.relationship import Relationship
from models.coach import CoachConversation
from models import db
from services.ai_service import AIService

coach_bp = Blueprint("coach", __name__)


@coach_bp.route("/coach")
def coach_page():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    return render_template("coach.html")


@coach_bp.route("/api/coach", methods=["POST"])
def api_coach():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "reply": "Session expired. Please log in again."}), 401
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"ok": False, "reply": "Please enter your relationship question."}), 400

    rel = Relationship.query.filter_by(user_id=user_id, status="active").order_by(Relationship.id.desc()).first()
    context = {"score":"Not available","category":"Not available","communication":"Not available","weaknesses":"No saved compatibility result yet"}
    if rel:
        comp = CompatibilityResult.query.filter_by(relationship_id=rel.id).order_by(CompatibilityResult.id.desc()).first()
        chat = ChatAnalysis.query.filter_by(relationship_id=rel.id).order_by(ChatAnalysis.id.desc()).first()
        if comp:
            context.update(score=round(float(comp.overall_score or 0),1), category=comp.category or "Not available", communication=round(float(comp.communication_score or 0),1), weaknesses=f"Values {comp.values_score or 0}%, lifestyle {comp.lifestyle_score or 0}%, communication {comp.communication_score or 0}%")
        if chat and not comp:
            context["communication"] = round(float(chat.communication_score or 0),1)

    reply = AIService.generate_coach_reply(message, context)
    try:
        db.session.add(CoachConversation(user_id=user_id, relationship_id=rel.id if rel else None, user_message=message, ai_reply=reply))
        db.session.commit()
    except Exception:
        db.session.rollback()
    return jsonify({"ok": True, "reply": reply})
