import json

from flask import Blueprint, redirect, render_template, session, url_for

from models.astrology import AstrologyProfile
from models.chat_analysis import ChatAnalysis
from models.compatibility import CompatibilityResult
from models.relationship import Relationship
from models.report import AIReport
from services.astrology_service import AstrologyService


report_bp = Blueprint("report", __name__)


@report_bp.route("/report/<int:relationship_id>")
def view_report(relationship_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    rel = Relationship.query.get_or_404(relationship_id)
    if rel.user_id != user_id:
        return "Unauthorized", 403

    comp = (
        CompatibilityResult.query
        .filter_by(relationship_id=rel.id)
        .order_by(CompatibilityResult.id.desc())
        .first()
    )
    ai_report_obj = (
        AIReport.query
        .filter_by(relationship_id=rel.id)
        .order_by(AIReport.id.desc())
        .first()
    )

    report_json = {}
    if ai_report_obj:
        try:
            report_json = json.loads(ai_report_obj.report_content)
        except (TypeError, ValueError):
            report_json = {}

    u_astro = AstrologyProfile.query.filter_by(user_id=rel.user_id).first()
    p_astro = AstrologyProfile.query.filter_by(user_id=rel.user2_id).first() if rel.user2_id else None

    astro_interp = None
    if u_astro and p_astro:
        astro_interp = AstrologyService.evaluate_astrology_compatibility(
            u_astro.zodiac_sign,
            p_astro.zodiac_sign,
        )

    chat_res = (
        ChatAnalysis.query
        .filter_by(relationship_id=rel.id)
        .order_by(ChatAnalysis.id.desc())
        .first()
    )

    return render_template(
        "report.html",
        relationship=rel,
        comp=comp,
        report=report_json,
        u_astro=u_astro,
        p_astro=p_astro,
        astro_interp=astro_interp,
        chat_res=chat_res,
    )
