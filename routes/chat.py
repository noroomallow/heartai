import json
import re
from collections import Counter
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from models import db
from models.chat_analysis import ChatAnalysis
from models.relationship import Relationship
from services.ai_service import AIService
from services.assessment_service import AssessmentService

chat_bp = Blueprint("chat", __name__)
WHATSAPP_PATTERN = re.compile(r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),\s*(\d{1,2}:\d{2}(?:\s?[APap][Mm])?)\s*-\s*([^:]+):\s*(.*)$")


def parse_whatsapp_chat(text):
    messages, current = [], None
    for raw in (text or "").splitlines():
        line = raw.rstrip()
        m = WHATSAPP_PATTERN.match(line)
        if m:
            if current: messages.append(current)
            current = {"date":m.group(1),"time":m.group(2),"sender":m.group(3).strip(),"message":m.group(4).strip()}
        elif current and line.strip():
            current["message"] += "\n" + line.strip()
    if current: messages.append(current)
    return messages


def clean_messages(messages):
    blocked = ["messages and calls are end-to-end encrypted","messages are end-to-end encrypted","only people in this chat can read","security code changed","joined using this group's invite link"]
    return [m for m in messages if not any(x in m["message"].lower() for x in blocked)]


def calculate_statistics(messages):
    counts = Counter(m["sender"] for m in messages)
    total = len(messages)
    if not total:
        return {"total_messages":0,"participants":[],"participant_counts":{},"participant_percentages":{},"conversation_start":None,"conversation_end":None,"average_message_length":0,"media_messages":0}
    media = sum("media omitted" in m["message"].lower() for m in messages)
    return {"total_messages":total,"participants":list(counts),"participant_counts":dict(counts),"participant_percentages":{p:round(c*100/total,2) for p,c in counts.items()},"conversation_start":messages[0]["date"]+" "+messages[0]["time"],"conversation_end":messages[-1]["date"]+" "+messages[-1]["time"],"average_message_length":round(sum(len(m["message"]) for m in messages)/total,2),"media_messages":media}


def format_chat_for_ai(messages):
    return "\n".join(f'{m["date"]}, {m["time"]} - {m["sender"]}: {m["message"]}' for m in messages)


def _load(value, default):
    try: return json.loads(value or "")
    except Exception: return default


@chat_bp.route("/chat-analysis", methods=["GET","POST"])
def chat_analysis():
    user_id = session.get("user_id")
    if not user_id: return redirect(url_for("auth.login"))

    if request.method == "POST":
        pasted = request.form.get("chat_text", "").strip()
        uploaded = request.files.get("chat_file")
        text = pasted
        if uploaded and uploaded.filename:
            if not uploaded.filename.lower().endswith(".txt"):
                flash("Please upload a WhatsApp .txt export file.", "danger")
                return redirect(url_for("chat.chat_analysis"))
            raw = uploaded.read()
            for enc in ("utf-8-sig","utf-16","utf-8","latin-1"):
                try:
                    text = raw.decode(enc); break
                except UnicodeDecodeError: continue
        if not text.strip():
            flash("Please upload a WhatsApp .txt file or paste your chat.", "warning")
            return redirect(url_for("chat.chat_analysis"))

        messages = clean_messages(parse_whatsapp_chat(text))
        if not messages:
            flash("No valid WhatsApp messages were detected. Use the original WhatsApp exported .txt file.", "danger")
            return redirect(url_for("chat.chat_analysis"))
        stats = calculate_statistics(messages)
        participants = stats["participants"]
        clean_text = format_chat_for_ai(messages)
        result = AIService.analyze_whatsapp_chat(clean_text, participants, stats)

        relationship = Relationship.query.filter_by(user_id=user_id, status="active").order_by(Relationship.id.desc()).first()
        try:
            record = ChatAnalysis(
                user_id=user_id,
                relationship_id=relationship.id if relationship else None,
                participants=json.dumps(participants, ensure_ascii=False),
                total_messages=stats["total_messages"],
                participant_statistics=json.dumps(stats, ensure_ascii=False),
                positive_percentage=float(result.get("positive_percentage",0)),
                neutral_percentage=float(result.get("neutral_percentage",0)),
                negative_percentage=float(result.get("negative_percentage",0)),
                communication_score=float(result.get("communication_score",0)),
                engagement_score=float(result.get("engagement_score",0)),
                emotional_score=float(result.get("emotional_score",0)),
                trust_score=float(result.get("trust_score",0)),
                compatibility_score=float(result.get("compatibility_score",0)),
                emotional_tone=str(result.get("emotional_tone","Neutral")),
                ai_summary=str(result.get("summary","")),
                ai_analysis_json=json.dumps(result, ensure_ascii=False),
                analysis=str(result.get("detailed_analysis", result.get("summary",""))),
                chat_text=clean_text,
            )
            db.session.add(record)
            db.session.commit()
            AssessmentService.calculate(user_id, relationship_id=relationship.id if relationship else None, save=True)
            flash("Chat analysis completed and saved successfully.", "success")
        except Exception as exc:
            db.session.rollback()
            print(f"Chat save error: {type(exc).__name__}: {exc}")
            flash("AI analysis was completed, but the result could not be saved. Check the database.", "warning")

        return render_template("chat_analysis.html", result=result, statistics=stats, participants=participants, chat_text=text)

    latest = ChatAnalysis.query.filter_by(user_id=user_id).order_by(ChatAnalysis.created_at.desc()).first()
    result = _load(latest.ai_analysis_json, None) if latest else None
    stats = _load(latest.participant_statistics, {}) if latest else {}
    participants = _load(latest.participants, []) if latest else []
    return render_template("chat_analysis.html", result=result, statistics=stats, participants=participants, chat_text=latest.chat_text if latest else "")


@chat_bp.route("/chat-analysis/latest")
def latest_analysis():
    user_id = session.get("user_id")
    if not user_id: return redirect(url_for("auth.login"))
    latest = ChatAnalysis.query.filter_by(user_id=user_id).order_by(ChatAnalysis.created_at.desc()).first()
    if not latest:
        flash("No WhatsApp chat analysis found.", "info")
        return redirect(url_for("chat.chat_analysis"))
    return render_template("chat_analysis.html", result=_load(latest.ai_analysis_json, {}), statistics=_load(latest.participant_statistics, {}), participants=_load(latest.participants, []), chat_text=latest.chat_text or "")
