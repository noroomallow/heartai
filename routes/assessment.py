import json
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from flask import Blueprint, redirect, render_template, session, url_for, send_file, flash
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)

from models import db
from models.user import User
from models.personality import PersonalityProfile
from models.compatibility import CompatibilityResult
from models.chat_analysis import ChatAnalysis
from models.astrology import AstrologyReading
from models.relationship_plan import DailyTask
from models.coach import CoachConversation
from models.assessment import AssessmentSnapshot
from models.report import AIReport
from services.assessment_service import AssessmentService
from services.astrology_service import AstrologyService
from services.recommendation_service import RecommendationService

assessment_bp = Blueprint("assessment", __name__)


def _safe(value):
    return "" if value is None else str(value)


def _json(value, default=None):
    if not value:
        return default if default is not None else {}
    try:
        return json.loads(value)
    except Exception:
        return default if default is not None else {}


def _list(value):
    if isinstance(value, list):
        return value
    return []


def _build_ai_content(assessment, user, relationship, astrology, chats, coach_history, tasks):
    comp = assessment.get("compatibility")
    personality = assessment.get("personality")
    chat = assessment.get("chat")

    scores = {
        "overall_score": assessment["overall_score"],
        "category": assessment["category"],
        "personality": assessment["personality_score"],
        "compatibility": assessment["compatibility_score"],
        "chat": assessment["chat_score"],
    }
    if comp:
        scores.update({
            "personality_dimension": comp.personality_score,
            "interests": comp.interests_score,
            "values": comp.values_score,
            "communication": comp.communication_score,
            "lifestyle": comp.lifestyle_score,
            "preferences": comp.preference_score,
        })

    astro_context = {}
    if astrology:
        astro_context = {
            "mode": astrology.mode,
            "person1": astrology.get_person1_data(),
            "person2": astrology.get_person2_data(),
            "combined": astrology.get_combined_data(),
        }

    chat_context = []
    for item in chats[:10]:
        chat_context.append({
            "date": item.created_at.isoformat() if item.created_at else "",
            "messages": item.total_messages,
            "communication": item.communication_score,
            "emotional": item.emotional_score,
            "trust": item.trust_score,
            "compatibility": item.compatibility_score,
            "tone": item.emotional_tone,
            "summary": item.ai_summary,
        })

    coach_context = [
        {
            "date": item.created_at.isoformat() if item.created_at else "",
            "question": item.user_message,
            "reply": item.ai_reply,
        }
        for item in coach_history[:10]
    ]

    plan_context = [
        {"day": t.day_number, "week": t.week_number, "title": t.title, "description": t.description}
        for t in tasks
    ]

    personality_context = {}
    if personality:
        personality_context = {
            "type": personality.personality_type,
            "overall": personality.overall_score,
            "communication": personality.communication_style,
            "emotional_openness": personality.emotional_openness,
            "conflict_style": personality.conflict_style,
            "trust": personality.trust_level,
            "social_preference": personality.social_preference,
            "relationship_expectation": personality.relationship_expectation,
        }

    extra = {
        "personality": personality_context,
        "astrology": astro_context,
        "chat_history": chat_context,
        "coach_history": coach_context,
        "plan": plan_context,
    }
    p1 = user.name if user else "Person A"
    p2 = relationship.partner_name if relationship else "Partner"
    return RecommendationService.get_full_report(scores, p1, p2, extra)


def _save_ai_report(relationship_id, content):
    if not relationship_id or not content:
        return
    try:
        obj = AIReport(
            relationship_id=relationship_id,
            report_type="comprehensive_relationship_report",
            report_content=json.dumps(content, ensure_ascii=False),
        )
        db.session.add(obj)
        db.session.commit()
    except Exception:
        db.session.rollback()


def _header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#ead7e8"))
    canvas.setLineWidth(0.6)
    canvas.line(15 * mm, height - 12 * mm, width - 15 * mm, height - 12 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#7b6b7c"))
    canvas.drawString(15 * mm, 8 * mm, "HeartAI | AI Love Compatibility & Relationship Advisor")
    canvas.drawRightString(width - 15 * mm, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _section(title, body, styles):
    return [
        Paragraph(escape(title), styles["SectionTitle"]),
        Paragraph(body, styles["Body"]),
        Spacer(1, 5 * mm),
    ]


def _bullets(items, styles):
    flow = []
    for item in _list(items):
        flow.append(Paragraph("• " + escape(_safe(item)), styles["Body"]))
    return flow


def _make_pdf(assessment, user, relationship, personality, compatibility, astrology, chats, coach_history, tasks, history, ai_content):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=18 * mm,
        bottomMargin=14 * mm,
        title="HeartAI Professional Relationship Report",
        author="HeartAI",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Cover", parent=styles["Title"], alignment=TA_CENTER, fontSize=25, leading=30, textColor=colors.HexColor("#6c3b78"), spaceAfter=5))
    styles.add(ParagraphStyle(name="CoverSub", parent=styles["BodyText"], alignment=TA_CENTER, fontSize=12, leading=17, textColor=colors.HexColor("#755f73"), spaceAfter=8))
    styles.add(ParagraphStyle(name="ScoreBig", parent=styles["Title"], alignment=TA_CENTER, fontSize=38, leading=42, textColor=colors.HexColor("#b84f91"), spaceAfter=4))
    styles.add(ParagraphStyle(name="ScoreCat", parent=styles["Heading2"], alignment=TA_CENTER, fontSize=14, textColor=colors.HexColor("#6c3b78"), spaceAfter=12))
    styles.add(ParagraphStyle(name="SectionTitle", parent=styles["Heading2"], fontSize=16, leading=20, textColor=colors.HexColor("#6c3b78"), spaceBefore=5, spaceAfter=5))
    styles.add(ParagraphStyle(name="SubTitle", parent=styles["Heading3"], fontSize=11.5, leading=15, textColor=colors.HexColor("#8e4f84"), spaceBefore=5, spaceAfter=3))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], fontSize=9.4, leading=14, textColor=colors.HexColor("#302a31"), spaceAfter=3))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=7.5, leading=10, textColor=colors.HexColor("#655b66")))
    styles.add(ParagraphStyle(name="CenterSmall", parent=styles["Small"], alignment=TA_CENTER))

    story = []
    p1 = user.name if user else "Person A"
    p2 = relationship.partner_name if relationship else "Partner"

    # Cover
    story += [Spacer(1, 25 * mm), Paragraph("HeartAI", styles["Cover"]), Paragraph("AI Love Compatibility & Relationship Advisor", styles["CoverSub"])]
    story += [Spacer(1, 12 * mm), Paragraph(escape(f"{p1}  |  {p2}"), styles["Cover"]), Paragraph("Professional Relationship Reflection Report", styles["CoverSub"])]
    story += [Spacer(1, 8 * mm), Paragraph(f"{assessment['overall_score']:.1f}%", styles["ScoreBig"]), Paragraph(escape(assessment["category"]), styles["ScoreCat"])]
    cover_table = Table([
        ["Generated", datetime.now().strftime("%d %B %Y, %I:%M %p")],
        ["Assessments completed", str(assessment["tests_completed"])],
        ["Relationship type", _safe(getattr(relationship, "relationship_type", "romantic"))],
    ], colWidths=[58 * mm, 95 * mm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f7eef6")),
        ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#dbc8d9")),
        ("PADDING", (0,0), (-1,-1), 7),
        ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#6c3b78")),
    ]))
    story += [cover_table, Spacer(1, 10 * mm), Paragraph("This report is a structured reflection tool. It does not predict relationship outcomes, and astrology is presented separately for entertainment and personal reflection.", styles["CenterSmall"]), PageBreak()]

    # Overall score and tests
    story += _section("1. Overall Relationship Score", f"The current overall score is <b>{assessment['overall_score']:.1f}%</b> and the current category is <b>{escape(assessment['category'])}</b>. The score uses completed assessments and normalizes their configured weights; missing assessments are not treated as zero.", styles)
    score_rows = [["Assessment", "Score", "Status"]]
    score_rows += [
        ["Personality Test", f"{assessment['personality_score']:.1f}%", "Completed" if personality else "Not completed"],
        ["Compatibility Test", f"{assessment['compatibility_score']:.1f}%", "Completed" if compatibility else "Not completed"],
        ["Chat AI Analysis", f"{assessment['chat_score']:.1f}%", "Completed" if assessment.get("chat") else "Not completed"],
    ]
    t = Table(score_rows, colWidths=[75*mm, 35*mm, 45*mm], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#6c3b78")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#d7c8d8")), ("PADDING", (0,0), (-1,-1), 6)]))
    story += [t, Spacer(1, 7*mm)]

    if history:
        story.append(Paragraph("Assessment History", styles["SubTitle"]))
        rows = [["Date", "Score", "Category"]]
        for h in history:
            rows.append([h.created_at.strftime("%d %b %Y") if h.created_at else "", f"{h.overall_score:.1f}%", _safe(h.category)])
        ht = Table(rows, colWidths=[45*mm, 35*mm, 75*mm], repeatRows=1)
        ht.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f3e8f3")), ("GRID", (0,0), (-1,-1), .3, colors.HexColor("#ddd0dd")), ("PADDING", (0,0), (-1,-1), 5)]))
        story += [ht, Spacer(1, 5*mm)]

    # Personality
    story.append(Paragraph("2. Personality Profile", styles["SectionTitle"]))
    if personality:
        story.append(Paragraph(f"Personality type: <b>{escape(_safe(personality.personality_type) or 'Relationship Profile')}</b> | Overall personality score: <b>{float(personality.overall_score or 0):.1f}%</b>", styles["Body"]))
        rows = [["Dimension", "Score"], ["Communication", f"{float(personality.communication_style or 0):.1f}%"], ["Emotional openness", f"{float(personality.emotional_openness or 0):.1f}%"], ["Conflict handling", f"{float(personality.conflict_style or 0):.1f}%"], ["Trust", f"{float(personality.trust_level or 0):.1f}%"], ["Social preference", f"{float(personality.social_preference or 0):.1f}%"], ["Relationship expectations", f"{float(personality.relationship_expectation or 0):.1f}%"]]
        pt = Table(rows, colWidths=[95*mm, 45*mm], repeatRows=1)
        pt.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#8e4f84")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .3, colors.HexColor("#ddd0dd")), ("PADDING", (0,0), (-1,-1), 5)]))
        story += [pt, Spacer(1, 5*mm)]
        if personality.interests_text:
            story.append(Paragraph("Interests", styles["SubTitle"]))
            story.append(Paragraph(escape(_safe(personality.interests_text)), styles["Body"]))
        if personality.lifestyle_text:
            story.append(Paragraph("Lifestyle", styles["SubTitle"]))
            story.append(Paragraph(escape(_safe(personality.lifestyle_text)), styles["Body"]))
    else:
        story.append(Paragraph("Personality test has not been completed.", styles["Body"]))

    # Compatibility
    story += [PageBreak(), Paragraph("3. Compatibility Assessment", styles["SectionTitle"])]
    if compatibility:
        story.append(Paragraph(f"Overall compatibility: <b>{float(compatibility.overall_score or 0):.1f}%</b> — {escape(_safe(compatibility.category))}", styles["Body"]))
        rows = [["Dimension", "Score", "Weight"]]
        dims = [("Personality", compatibility.personality_score, "25%"), ("Shared interests", compatibility.interests_score, "15%"), ("Values", compatibility.values_score, "20%"), ("Communication", compatibility.communication_score, "20%"), ("Lifestyle", compatibility.lifestyle_score, "10%"), ("Preferences", compatibility.preference_score, "10%")]
        for name, value, weight in dims:
            rows.append([name, f"{float(value or 0):.1f}%", weight])
        ct = Table(rows, colWidths=[75*mm, 40*mm, 30*mm], repeatRows=1)
        ct.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#6c3b78")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#d7c8d8")), ("PADDING", (0,0), (-1,-1), 5)]))
        story += [ct, Spacer(1, 5*mm), Paragraph("The compatibility score is calculated by Python from the questionnaire; AI is used to explain the result, not to determine the numerical score.", styles["Small"])]
    else:
        story.append(Paragraph("Compatibility test has not been completed.", styles["Body"]))

    # Astrology
    story.append(Paragraph("4. Astrology Insights", styles["SectionTitle"]))
    story.append(Paragraph("Astrology-based interpretation for entertainment and personal reflection. It does not scientifically predict relationship outcomes and is not included in the main compatibility score.", styles["Small"]))
    if astrology:
        p1_data = astrology.get_person1_data() or {}
        p2_data = astrology.get_person2_data() or {}
        combined = astrology.get_combined_data() or {}
        story.append(Paragraph(f"<b>{escape(_safe(astrology.person1_name))}</b>: {escape(_safe(p1_data.get('zodiac_sign') or p1_data.get('rasi') or 'Not available'))}", styles["Body"]))
        if astrology.person2_name:
            story.append(Paragraph(f"<b>{escape(_safe(astrology.person2_name))}</b>: {escape(_safe(p2_data.get('zodiac_sign') or p2_data.get('rasi') or 'Not available'))}", styles["Body"]))
        interp = AstrologyService.evaluate_astrology_compatibility(p1_data.get("zodiac_sign", ""), p2_data.get("zodiac_sign", "")) if p2_data else "A single-person astrology profile is available."
        story.append(Paragraph(escape(_safe(interp)), styles["Body"]))
        if combined:
            story.append(Paragraph("Couple astrology details", styles["SubTitle"]))
            for key in ("summary", "compatibility", "relationship", "advice", "interpretation"):
                if combined.get(key):
                    story.append(Paragraph(f"<b>{escape(key.replace('_', ' ').title())}:</b> {escape(_safe(combined[key]))}", styles["Body"]))
    else:
        story.append(Paragraph("No astrology reading has been saved yet.", styles["Body"]))

    # 30 day plan
    story += [PageBreak(), Paragraph("5. 30-Day Relationship Bonding Plan", styles["SectionTitle"])]
    if tasks:
        story.append(Paragraph("The plan mixes communication, dating, shared experiences, personal style, movies, cooking, surprises, hobbies, memories, future planning and relationship check-ins. Activities are designed to be mutual and adaptable to your budget and schedule.", styles["Body"]))
        for task in tasks:
            status = "Completed" if task.completed else "Pending"
            block = [Paragraph(f"Day {task.day_number} | Week {task.week_number} | <b>{escape(_safe(task.title))}</b> | {status}", styles["SubTitle"]), Paragraph(escape(_safe(task.description)), styles["Body"])]
            story.append(KeepTogether(block))
    else:
        story.append(Paragraph("No active 30-day plan is available. Complete an assessment and create a relationship profile first.", styles["Body"]))

    # Chat history
    story += [PageBreak(), Paragraph("6. Chat AI Analysis History", styles["SectionTitle"])]
    if chats:
        for i, chat in enumerate(chats, 1):
            story.append(Paragraph(f"Chat Analysis #{i} — {chat.created_at.strftime('%d %b %Y, %I:%M %p') if chat.created_at else ''}", styles["SubTitle"]))
            story.append(Paragraph(f"Messages: {chat.total_messages or 0} | Positive: {float(chat.positive_percentage or 0):.1f}% | Neutral: {float(chat.neutral_percentage or 0):.1f}% | Negative: {float(chat.negative_percentage or 0):.1f}%", styles["Body"]))
            story.append(Paragraph(f"Communication: {float(chat.communication_score or 0):.1f}% | Emotional: {float(chat.emotional_score or 0):.1f}% | Trust: {float(chat.trust_score or 0):.1f}% | Compatibility: {float(chat.compatibility_score or 0):.1f}% | Tone: {escape(_safe(chat.emotional_tone))}", styles["Body"]))
            if chat.ai_summary:
                story.append(Paragraph("AI summary: " + escape(_safe(chat.ai_summary)), styles["Body"]))
    else:
        story.append(Paragraph("No chat analyses have been recorded.", styles["Body"]))

    # Coach
    story.append(Paragraph("7. AI Relationship Coach", styles["SectionTitle"]))
    if coach_history:
        for item in coach_history:
            story.append(Paragraph(f"Question — {item.created_at.strftime('%d %b %Y, %I:%M %p') if item.created_at else ''}", styles["SubTitle"]))
            story.append(Paragraph(escape(_safe(item.user_message)), styles["Body"]))
            story.append(Paragraph("AI Coach response:", styles["Small"]))
            story.append(Paragraph(escape(_safe(item.ai_reply)), styles["Body"]))
    else:
        story.append(Paragraph("No saved AI Coach conversations yet. The Coach is available from the HeartAI dashboard.", styles["Body"]))

    # Final AI content LAST
    story += [PageBreak(), Paragraph("8. Final AI Relationship Report", styles["SectionTitle"]), Paragraph("This final section is generated by the HeartAI AI service from the available assessment, personality, compatibility, astrology, chat-analysis, coach and plan context. It is guidance for reflection rather than a prediction.", styles["Small"]), Spacer(1, 4*mm)]
    story.append(Paragraph("Overall Summary", styles["SubTitle"]))
    story.append(Paragraph(escape(_safe(ai_content.get("summary"))), styles["Body"]))
    story.append(Paragraph("Compatibility Explanation", styles["SubTitle"]))
    story.append(Paragraph(escape(_safe(ai_content.get("compatibility_explanation"))), styles["Body"]))
    for title, key in [("Relationship Strengths", "strengths"), ("Potential Challenges", "challenges"), ("Personalized Recommendations", "recommendations"), ("Communication Suggestions", "communication_tips"), ("Date & Bonding Ideas", "date_ideas"), ("Recommended Next Steps", "next_steps")]:
        story.append(Paragraph(title, styles["SubTitle"]))
        story += _bullets(ai_content.get(key, []), styles)
        story.append(Spacer(1, 2*mm))

    story += [Spacer(1, 7*mm), Paragraph("Privacy & Safety", styles["SectionTitle"]), Paragraph("HeartAI uses information voluntarily supplied by users. Only analyze conversations you are authorized to share. HeartAI does not guarantee relationship outcomes, does not present astrology as scientific, and is not a substitute for professional support.", styles["Small"])]

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    buffer.seek(0)
    return buffer


@assessment_bp.route("/assessment")
def assessment_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    assessment = AssessmentService.calculate(user_id, save=False)
    if assessment:
        AssessmentService.ensure_plan(assessment)
    return redirect(url_for("dashboard.index"))


@assessment_bp.route("/assessment/report")
def assessment_report():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    user = User.query.get(user_id)
    assessment = AssessmentService.calculate(user_id, save=False)
    if not assessment:
        flash("Complete at least one assessment first.", "info")
        return redirect(url_for("dashboard.index"))
    plan = AssessmentService.ensure_plan(assessment)
    tasks = DailyTask.query.filter_by(plan_id=plan.id).order_by(DailyTask.day_number.asc()).all() if plan else []
    chats = ChatAnalysis.query.filter_by(user_id=user_id).order_by(ChatAnalysis.created_at.desc()).all()
    coach_history = CoachConversation.query.filter_by(user_id=user_id).order_by(CoachConversation.created_at.desc()).all()
    personality = PersonalityProfile.query.filter_by(user_id=user_id).first()
    relationship = assessment.get("relationship")
    compatibility = assessment.get("compatibility")
    astrology = AstrologyReading.query.filter_by(user_id=user_id).order_by(AstrologyReading.id.desc()).first()
    history = AssessmentSnapshot.query.filter_by(user_id=user_id).order_by(AssessmentSnapshot.created_at.desc()).limit(10).all()
    ai_content = _build_ai_content(assessment, user, relationship, astrology, chats, coach_history, tasks)
    if relationship:
        _save_ai_report(relationship.id, ai_content)
    return render_template("assessment_report.html", user=user, assessment=assessment, plan=plan, tasks=tasks, chats=chats, coach_history=coach_history, personality=personality, relationship=relationship, compatibility=compatibility, astrology=astrology, history=history, ai_content=ai_content)


@assessment_bp.route("/assessment/report/pdf")
def assessment_report_pdf():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    user = User.query.get(user_id)
    assessment = AssessmentService.calculate(user_id, save=False)
    if not assessment:
        flash("Complete at least one assessment first.", "info")
        return redirect(url_for("dashboard.index"))
    plan = AssessmentService.ensure_plan(assessment)
    tasks = DailyTask.query.filter_by(plan_id=plan.id).order_by(DailyTask.day_number.asc()).all() if plan else []
    chats = ChatAnalysis.query.filter_by(user_id=user_id).order_by(ChatAnalysis.created_at.desc()).all()
    coach_history = CoachConversation.query.filter_by(user_id=user_id).order_by(CoachConversation.created_at.desc()).all()
    personality = PersonalityProfile.query.filter_by(user_id=user_id).first()
    relationship = assessment.get("relationship")
    compatibility = assessment.get("compatibility")
    astrology = AstrologyReading.query.filter_by(user_id=user_id).order_by(AstrologyReading.id.desc()).first()
    history = AssessmentSnapshot.query.filter_by(user_id=user_id).order_by(AssessmentSnapshot.created_at.desc()).limit(10).all()

    ai_content = _build_ai_content(assessment, user, relationship, astrology, chats, coach_history, tasks)
    if relationship:
        _save_ai_report(relationship.id, ai_content)

    pdf = _make_pdf(assessment, user, relationship, personality, compatibility, astrology, chats, coach_history, tasks, history, ai_content)
    return send_file(pdf, mimetype="application/pdf", as_attachment=True, download_name="HeartAI_Professional_Relationship_Report.pdf")
