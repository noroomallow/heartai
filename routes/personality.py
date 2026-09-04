import json
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from services.assessment_service import AssessmentService
from models import db
from models.user import User
from models.personality import PersonalityProfile


personality_bp = Blueprint("personality", __name__)


# ---------------------------------------------------------
# 50-QUESTION PERSONALITY TEST
# ---------------------------------------------------------

QUESTIONS = [
    {
        "id": "q1",
        "text": "How easily do you start a conversation with someone new?",
        "category": "communication"
    },
    {
        "id": "q2",
        "text": "How comfortable are you expressing your feelings?",
        "category": "emotional_openness"
    },
    {
        "id": "q3",
        "text": "When you disagree with someone, how calmly do you respond?",
        "category": "conflict_handling"
    },
    {
        "id": "q4",
        "text": "How easily do you trust someone after getting to know them?",
        "category": "trust"
    },
    {
        "id": "q5",
        "text": "How much do you enjoy spending time with other people?",
        "category": "social"
    },
    {
        "id": "q6",
        "text": "How important is emotional connection in a relationship?",
        "category": "relationship"
    },
    {
        "id": "q7",
        "text": "How often do you listen carefully when someone talks?",
        "category": "communication"
    },
    {
        "id": "q8",
        "text": "How comfortable are you telling someone when something bothers you?",
        "category": "emotional_openness"
    },
    {
        "id": "q9",
        "text": "How willing are you to compromise during an argument?",
        "category": "conflict_handling"
    },
    {
        "id": "q10",
        "text": "How reliable do you think people are generally?",
        "category": "trust"
    },
    {
        "id": "q11",
        "text": "How comfortable are you in a group of people?",
        "category": "social"
    },
    {
        "id": "q12",
        "text": "How important is loyalty to you in a relationship?",
        "category": "relationship"
    },
    {
        "id": "q13",
        "text": "How clearly do you explain your thoughts?",
        "category": "communication"
    },
    {
        "id": "q14",
        "text": "How easily can you show affection?",
        "category": "emotional_openness"
    },
    {
        "id": "q15",
        "text": "When angry, how well can you control your words?",
        "category": "conflict_handling"
    },
    {
        "id": "q16",
        "text": "How comfortable are you sharing personal information with someone you trust?",
        "category": "trust"
    },
    {
        "id": "q17",
        "text": "How much do you enjoy meeting new people?",
        "category": "social"
    },
    {
        "id": "q18",
        "text": "How important is mutual support in a relationship?",
        "category": "relationship"
    },
    {
        "id": "q19",
        "text": "How well do you communicate when you are busy?",
        "category": "communication"
    },
    {
        "id": "q20",
        "text": "How comfortable are you discussing emotional problems?",
        "category": "emotional_openness"
    },
    {
        "id": "q21",
        "text": "How quickly do you try to solve a disagreement?",
        "category": "conflict_handling"
    },
    {
        "id": "q22",
        "text": "How confident are you that your close friends will support you?",
        "category": "trust"
    },
    {
        "id": "q23",
        "text": "How much personal space do you normally prefer?",
        "category": "social"
    },
    {
        "id": "q24",
        "text": "How important is honesty in a relationship?",
        "category": "relationship"
    },
    {
        "id": "q25",
        "text": "How often do you ask others about their feelings?",
        "category": "communication"
    },
    {
        "id": "q26",
        "text": "How easily do you admit that you are emotionally hurt?",
        "category": "emotional_openness"
    },
    {
        "id": "q27",
        "text": "How well do you handle criticism from someone close to you?",
        "category": "conflict_handling"
    },
    {
        "id": "q28",
        "text": "How strongly do you value keeping promises?",
        "category": "trust"
    },
    {
        "id": "q29",
        "text": "How much do you enjoy social activities?",
        "category": "social"
    },
    {
        "id": "q30",
        "text": "How important is commitment to you?",
        "category": "relationship"
    },
    {
        "id": "q31",
        "text": "How often do you communicate when you miss someone?",
        "category": "communication"
    },
    {
        "id": "q32",
        "text": "How comfortable are you saying 'I love you' or similar emotional expressions?",
        "category": "emotional_openness"
    },
    {
        "id": "q33",
        "text": "How willing are you to forgive after an argument?",
        "category": "conflict_handling"
    },
    {
        "id": "q34",
        "text": "How easily can you depend on someone you trust?",
        "category": "trust"
    },
    {
        "id": "q35",
        "text": "How much do you enjoy being around your partner or friends?",
        "category": "social"
    },
    {
        "id": "q36",
        "text": "How important is spending quality time together?",
        "category": "relationship"
    },
    {
        "id": "q37",
        "text": "How good are you at explaining misunderstandings?",
        "category": "communication"
    },
    {
        "id": "q38",
        "text": "How comfortable are you showing vulnerability?",
        "category": "emotional_openness"
    },
    {
        "id": "q39",
        "text": "How patient are you during disagreements?",
        "category": "conflict_handling"
    },
    {
        "id": "q40",
        "text": "How strongly do you believe trust must be earned?",
        "category": "trust"
    },
    {
        "id": "q41",
        "text": "How comfortable are you balancing social time and alone time?",
        "category": "social"
    },
    {
        "id": "q42",
        "text": "How important is emotional understanding from your partner?",
        "category": "relationship"
    },
    {
        "id": "q43",
        "text": "How often do you communicate your expectations clearly?",
        "category": "communication"
    },
    {
        "id": "q44",
        "text": "How easily do you understand and recognize your own emotions?",
        "category": "emotional_openness"
    },
    {
        "id": "q45",
        "text": "How willing are you to find a solution that works for both people?",
        "category": "conflict_handling"
    },
    {
        "id": "q46",
        "text": "How strongly do you value consistency in someone's behavior?",
        "category": "trust"
    },
    {
        "id": "q47",
        "text": "How comfortable are you meeting your partner's friends or family?",
        "category": "social"
    },
    {
        "id": "q48",
        "text": "How important is respect in a relationship?",
        "category": "relationship"
    },
    {
        "id": "q49",
        "text": "How often do you check whether the other person is okay?",
        "category": "communication"
    },
    {
        "id": "q50",
        "text": "How strongly do you want a long-term meaningful relationship?",
        "category": "relationship"
    }
]


OPTIONS = [
    (1, "Never / Very Low"),
    (2, "Rarely / Low"),
    (3, "Sometimes / Moderate"),
    (4, "Often / High"),
    (5, "Always / Very High")
]


def score_label(score):
    if score >= 80:
        return "Excellent"
    elif score >= 65:
        return "Strong"
    elif score >= 50:
        return "Balanced"
    elif score >= 35:
        return "Needs Improvement"
    return "Low"


def calculate_scores(form_data):
    category_values = {
        "communication": [],
        "emotional_openness": [],
        "conflict_handling": [],
        "trust": [],
        "social": [],
        "relationship": []
    }

    for question in QUESTIONS:
        question_id = question["id"]
        category = question["category"]

        value = form_data.get(question_id)

        if value is None:
            continue

        try:
            value = int(value)
        except (ValueError, TypeError):
            continue

        if value < 1 or value > 5:
            continue

        category_values[category].append(value)

    scores = {}

    for category, values in category_values.items():
        if values:
            average = sum(values) / len(values)
            scores[category] = round((average - 1) * 25, 1)
        else:
            scores[category] = 0.0

    # Overall score is the actual average of all six categories.
    overall = round(
        sum(scores.values()) / len(scores),
        1
    )

    return scores, overall


def personality_description(overall):
    if overall >= 85:
        return "Highly Balanced Personality"
    elif overall >= 70:
        return "Strong Personality"
    elif overall >= 55:
        return "Balanced Personality"
    elif overall >= 40:
        return "Developing Personality"
    return "Needs Personal Growth"


@personality_bp.route("/personality", methods=["GET", "POST"])
def questionnaire():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        # Make sure all 50 questions were answered.
        missing_questions = []

        for question in QUESTIONS:
            if not request.form.get(question["id"]):
                missing_questions.append(question["id"])

        if missing_questions:
            flash(
                f"Please answer all 50 questions. "
                f"{len(missing_questions)} question(s) are unanswered.",
                "error"
            )

            return render_template(
                "personality.html",
                questions=QUESTIONS,
                options=OPTIONS
            )

        scores, overall = calculate_scores(request.form)

        interests = request.form.get("interests", "").strip()
        lifestyle = request.form.get("lifestyle", "").strip()

        profile = PersonalityProfile.query.filter_by(
            user_id=user_id
        ).first()

        if not profile:
            profile = PersonalityProfile(user_id=user_id)

        profile.communication_style = scores["communication"]
        profile.emotional_openness = scores["emotional_openness"]
        profile.conflict_style = scores["conflict_handling"]
        profile.trust_level = scores["trust"]
        profile.social_preference = scores["social"]
        profile.relationship_expectation = scores["relationship"]

        profile.interests_text = interests
        profile.lifestyle_text = lifestyle

        # Save overall score if the model contains this field.
        if hasattr(profile, "overall_score"):
            profile.overall_score = overall

        if hasattr(profile, "personality_type"):
            profile.personality_type = personality_description(overall)

        # Save raw answers when the model supports it.
        if hasattr(profile, "answers_json"):
            profile.answers_json = json.dumps(
                {
                    question["id"]: int(request.form.get(question["id"]))
                    for question in QUESTIONS
                }
            )

        db.session.add(profile)
        db.session.commit()

        # Save an overall snapshot when a relationship already exists.
        AssessmentService.calculate(user_id, save=True)

        flash(
            "Personality assessment completed successfully!",
            "success"
        )

        return redirect(
            url_for("personality.personality_result")
        )

    return render_template(
        "personality.html",
        questions=QUESTIONS,
        options=OPTIONS
    )


@personality_bp.route("/personality/result")
def personality_result():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)

    profile = PersonalityProfile.query.filter_by(
        user_id=user_id
    ).first()

    if not profile:
        flash(
            "Please complete the personality test first.",
            "warning"
        )
        return redirect(
            url_for("personality.questionnaire")
        )

    scores = {
        "communication": float(
            profile.communication_style or 0
        ),
        "emotional_openness": float(
            profile.emotional_openness or 0
        ),
        "conflict_handling": float(
            profile.conflict_style or 0
        ),
        "trust": float(
            profile.trust_level or 0
        ),
        "social": float(
            profile.social_preference or 0
        ),
        "relationship": float(
            profile.relationship_expectation or 0
        )
    }

    overall = round(
        sum(scores.values()) / len(scores),
        1
    )

    personality_type = personality_description(overall)

    return render_template(
        "personality_result.html",
        user=user,
        profile=profile,
        scores=scores,
        overall=overall,
        personality_type=personality_type
    )


@personality_bp.route("/profile", methods=["GET", "POST"])
def profile():
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("auth.login"))

    profile_data = PersonalityProfile.query.filter_by(
        user_id=user_id
    ).first()

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        if name:
            user.name = name

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(
            url_for("personality.profile")
        )

    return render_template(
        "profile.html",
        user=user,
        p_profile=profile_data
    )

