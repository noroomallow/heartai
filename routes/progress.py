from datetime import datetime

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from models import db
from models.compatibility import CompatibilityResult
from models.progress import ProgressTracking
from models.relationship import Relationship
from models.relationship_plan import DailyTask, RelationshipPlan
from services.assessment_service import AssessmentService


progress_bp = Blueprint("progress", __name__)


def current_relationship(user_id):
    return (
        Relationship.query
        .filter_by(user_id=user_id, status="active")
        .order_by(Relationship.id.desc())
        .first()
    )


@progress_bp.route("/plan")
def plan_view():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    rel = current_relationship(user_id)
    if not rel:
        return redirect(url_for("compatibility.partner"))

    plan = (
        RelationshipPlan.query
        .filter_by(relationship_id=rel.id, status="active")
        .order_by(RelationshipPlan.id.desc())
        .first()
    )

    if not plan:
        assessment = AssessmentService.calculate(user_id, relationship_id=rel.id, save=False)
        if assessment:
            plan = AssessmentService.ensure_plan(assessment)
    tasks = (
        DailyTask.query
        .filter_by(plan_id=plan.id)
        .order_by(DailyTask.day_number.asc())
        .all()
        if plan else []
    )

    return render_template("relationship_plan.html", plan=plan, tasks=tasks)


@progress_bp.route("/api/task/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    task = DailyTask.query.get_or_404(task_id)
    plan = RelationshipPlan.query.get(task.plan_id)
    rel = current_relationship(user_id)

    if not plan or not rel or plan.relationship_id != rel.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    task.completed = not task.completed
    task.completed_at = datetime.utcnow() if task.completed else None
    db.session.commit()
    return jsonify({"success": True, "completed": task.completed})


@progress_bp.route("/progress")
def progress_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    rel = current_relationship(user_id)
    if not rel:
        return redirect(url_for("compatibility.partner"))

    history = (
        ProgressTracking.query
        .filter_by(relationship_id=rel.id)
        .order_by(ProgressTracking.recorded_at.asc())
        .all()
    )
    comp = (
        CompatibilityResult.query
        .filter_by(relationship_id=rel.id)
        .order_by(CompatibilityResult.id.desc())
        .first()
    )

    return render_template("progress.html", rel=rel, history=history, comp=comp)
