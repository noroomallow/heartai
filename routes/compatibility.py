
import json

from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
)

from models import db
from models.personality import PersonalityProfile
from models.relationship import Relationship
from models.compatibility import CompatibilityResult
from services.assessment_service import AssessmentService


compatibility_bp = Blueprint("compatibility", __name__)


# ============================================================
# 30 COMPATIBILITY QUESTIONS
# ============================================================

COMPATIBILITY_QUESTIONS = [
    {
        "id": 1,
        "question": "How important is honest communication in a relationship?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 2,
        "question": "How often would you like to spend quality time with your partner?",
        "options": [
            "Very rarely",
            "Occasionally",
            "A few times a week",
            "Almost every day",
            "Every day",
        ],
    },
    {
        "id": 3,
        "question": "When you are upset, what do you prefer?",
        "options": [
            "Be completely alone",
            "Have some space first",
            "Talk later",
            "Talk after calming down",
            "Talk immediately",
        ],
    },
    {
        "id": 4,
        "question": "How important is trust to you?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 5,
        "question": "How do you usually handle disagreements?",
        "options": [
            "Avoid them",
            "Stay quiet",
            "Discuss calmly later",
            "Discuss immediately",
            "Talk openly until we solve it",
        ],
    },
    {
        "id": 6,
        "question": "How comfortable are you expressing your feelings?",
        "options": [
            "Not comfortable",
            "Slightly comfortable",
            "Sometimes comfortable",
            "Very comfortable",
            "Extremely comfortable",
        ],
    },
    {
        "id": 7,
        "question": "How important is personal space in a relationship?",
        "options": [
            "I need a lot",
            "I need quite a lot",
            "A balanced amount",
            "I prefer little space",
            "I prefer almost no space",
        ],
    },
    {
        "id": 8,
        "question": "How important is physical affection to you?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 9,
        "question": "How important is emotional support from your partner?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 10,
        "question": "How important is having common hobbies?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 11,
        "question": "What type of lifestyle do you prefer?",
        "options": [
            "Very quiet",
            "Mostly quiet",
            "Balanced",
            "Mostly active",
            "Very active",
        ],
    },
    {
        "id": 12,
        "question": "How social are you?",
        "options": [
            "Very private",
            "Mostly private",
            "Balanced",
            "Quite social",
            "Very social",
        ],
    },
    {
        "id": 13,
        "question": "How important is financial stability in a relationship?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 14,
        "question": "How do you prefer to manage money?",
        "options": [
            "Spend freely",
            "Mostly spend",
            "Balance spending and saving",
            "Mostly save",
            "Save very carefully",
        ],
    },
    {
        "id": 15,
        "question": "How important is career growth to you?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 16,
        "question": "How important is family involvement in your relationship?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 17,
        "question": "How important is marriage or long-term commitment to you?",
        "options": [
            "Not important",
            "Not sure",
            "Somewhat important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 18,
        "question": "How important is having children in the future?",
        "options": [
            "Definitely not",
            "Probably not",
            "Not sure",
            "Probably yes",
            "Definitely yes",
        ],
    },
    {
        "id": 19,
        "question": "How adventurous are you?",
        "options": [
            "Not adventurous",
            "Slightly adventurous",
            "Moderately adventurous",
            "Very adventurous",
            "Extremely adventurous",
        ],
    },
    {
        "id": 20,
        "question": "How important is travelling together?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 21,
        "question": "How do you prefer to show love?",
        "options": [
            "Words",
            "Quality time",
            "Gifts",
            "Acts of service",
            "Physical affection",
        ],
    },
    {
        "id": 22,
        "question": "How do you prefer your partner to show love?",
        "options": [
            "Words",
            "Quality time",
            "Gifts",
            "Acts of service",
            "Physical affection",
        ],
    },
    {
        "id": 23,
        "question": "How important is humour in your relationship?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 24,
        "question": "How quickly do you forgive after an argument?",
        "options": [
            "Very slowly",
            "Slowly",
            "It depends",
            "Quickly",
            "Very quickly",
        ],
    },
    {
        "id": 25,
        "question": "How important is independence in a relationship?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 26,
        "question": "How comfortable are you discussing future plans?",
        "options": [
            "Not comfortable",
            "Slightly comfortable",
            "Sometimes comfortable",
            "Very comfortable",
            "Extremely comfortable",
        ],
    },
    {
        "id": 27,
        "question": "How important is supporting your partner's career or education?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 28,
        "question": "How important is equality in making relationship decisions?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 29,
        "question": "How important is solving problems together?",
        "options": [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important",
            "Extremely important",
        ],
    },
    {
        "id": 30,
        "question": "What matters most for a long-lasting relationship?",
        "options": [
            "Trust",
            "Communication",
            "Love",
            "Respect",
            "All of these",
        ],
    },
]


# ============================================================
# START COUPLE TEST
# ============================================================

@compatibility_bp.route("/compatibility/test")
def compatibility_test():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth.login"))

    # Start with the current user
    session["compatibility_step"] = "user"

    # Remove previous temporary answers
    session.pop("compatibility_user_answers", None)
    session.pop("compatibility_partner_answers", None)

    return render_template(
        "compatibility_test.html",
        questions=COMPATIBILITY_QUESTIONS,
        person="You",
        person_number=1,
    )


# ============================================================
# SAVE USER / PARTNER ANSWERS
# ============================================================

@compatibility_bp.route("/compatibility/test/submit", methods=["POST"])
def submit_compatibility_test():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth.login"))

    answers = {}

    # Validate all 30 questions
    for question in COMPATIBILITY_QUESTIONS:

        question_id = str(question["id"])

        answer = request.form.get(f"q_{question_id}")

        if not answer:
            flash(
                f"Please answer question {question_id}.",
                "error",
            )

            person = session.get(
                "compatibility_step",
                "user",
            )

            return render_template(
                "compatibility_test.html",
                questions=COMPATIBILITY_QUESTIONS,
                person="Your Partner" if person == "partner" else "You",
                person_number=2 if person == "partner" else 1,
            )

        try:
            answer_value = int(answer)

            if answer_value < 1 or answer_value > 5:
                raise ValueError

            answers[question_id] = answer_value

        except ValueError:

            flash(
                "Invalid answer detected. Please try again.",
                "error",
            )

            return redirect(
                url_for("compatibility.compatibility_test")
            )

    # --------------------------------------------------------
    # USER ANSWERS
    # --------------------------------------------------------

    if session.get("compatibility_step") == "user":

        session["compatibility_user_answers"] = answers
        session["compatibility_step"] = "partner"

        flash(
            "Your answers have been saved. Now your partner can answer.",
            "success",
        )

        return render_template(
            "compatibility_test.html",
            questions=COMPATIBILITY_QUESTIONS,
            person="Your Partner",
            person_number=2,
        )

    # --------------------------------------------------------
    # PARTNER ANSWERS
    # --------------------------------------------------------

    session["compatibility_partner_answers"] = answers

    user_answers = session.get(
        "compatibility_user_answers",
        {},
    )

    partner_answers = session.get(
        "compatibility_partner_answers",
        {},
    )

    # Calculate compatibility
    result = calculate_compatibility(
        user_answers,
        partner_answers,
    )

    # Save result
    relationship = (
        Relationship.query
        .filter_by(user_id=user_id, status="active")
        .order_by(Relationship.id.desc())
        .first()
    )

    if relationship is None:
        relationship = Relationship(
            user_id=user_id,
            partner_name="Partner",
            relationship_type="romantic",
            status="active"
        )
        db.session.add(relationship)
        db.session.flush()

    compatibility_record = CompatibilityResult(
        relationship_id=relationship.id,
        personality_score=result["overall_score"],
        interests_score=result["overall_score"],
        values_score=result["overall_score"],
        communication_score=result["overall_score"],
        lifestyle_score=result["overall_score"],
        preference_score=result["overall_score"],
        overall_score=result["overall_score"],
        category=result["category"]
    )
    db.session.add(compatibility_record)

    profile = PersonalityProfile.query.filter_by(
        user_id=user_id
    ).first()

    if profile:

        profile.compatibility_score = result["overall_score"]
        profile.compatibility_data = json.dumps(
            result,
            ensure_ascii=False,
        )

        db.session.commit()

    # Clear temporary session data
    session.pop("compatibility_step", None)
    session.pop("compatibility_user_answers", None)
    session.pop("compatibility_partner_answers", None)

    return render_template(
        "compatibility_result.html",
        result=result,
    )


# ============================================================
# PARTNER PAGE
# ============================================================

@compatibility_bp.route("/partner", methods=["GET", "POST"])
def partner():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth.login"))

    relationship = (
        Relationship.query
        .filter_by(user_id=user_id)
        .order_by(Relationship.id.desc())
        .first()
    )

    if request.method == "POST":

        partner_name = request.form.get("partner_name", "Partner").strip()
        partner_email = request.form.get("partner_email", "").strip()
        relationship_type = request.form.get("relationship_type", "romantic").strip()

        if not partner_name:
            flash("Partner name is required.", "error")
            return redirect(url_for("compatibility.partner"))

        if relationship is None:
            relationship = Relationship(
                user_id=user_id,
                partner_name=partner_name,
                partner_email=partner_email or None,
                relationship_type=relationship_type or "romantic",
                status="active"
            )
            db.session.add(relationship)
        else:
            relationship.partner_name = partner_name
            relationship.partner_email = partner_email or None
            relationship.relationship_type = relationship_type or "romantic"
            relationship.status = "active"

        db.session.commit()
        flash("Partner details saved successfully.", "success")
        return redirect(url_for("compatibility.compatibility_test"))

    return render_template("partner.html", relationship=relationship)


# ============================================================
# COMPATIBILITY CALCULATION
# ============================================================

def calculate_compatibility(
    user_answers,
    partner_answers,
):

    matches = []
    differences = []

    total_difference = 0

    for question in COMPATIBILITY_QUESTIONS:

        question_id = str(question["id"])

        user_value = int(
            user_answers.get(question_id, 3)
        )

        partner_value = int(
            partner_answers.get(question_id, 3)
        )

        difference = abs(
            user_value - partner_value
        )

        total_difference += difference

        # 0 difference = 100%
        # 4 difference = 0%
        match_percentage = round(
            100 - (difference * 25)
        )

        item = {
            "question": question["question"],
            "you": user_value,
            "partner": partner_value,
            "match": match_percentage,
        }

        if difference <= 1:
            matches.append(item)
        else:
            differences.append(item)

    # 30 questions × maximum difference 4
    maximum_difference = 30 * 4

    overall_score = round(
        100 -
        (
            total_difference /
            maximum_difference
        ) * 100
    )

    overall_score = max(
        0,
        min(
            100,
            overall_score,
        ),
    )

    # Relationship category
    if overall_score >= 90:
        category = "Exceptional Connection"
    elif overall_score >= 80:
        category = "Strong Compatibility"
    elif overall_score >= 70:
        category = "Good Compatibility"
    elif overall_score >= 60:
        category = "Growing Compatibility"
    elif overall_score >= 50:
        category = "Needs Understanding"
    else:
        category = "Different Perspectives"

    # Direction
    if overall_score >= 75:
        direction = "🟢 You are mostly walking in the same direction."
    elif overall_score >= 55:
        direction = "🟡 You share some important goals, but there are areas to understand."
    else:
        direction = "🔵 You have meaningful differences that may need open communication."

    return {
        "overall_score": overall_score,
        "category": category,
        "direction": direction,
        "common_count": len(matches),
        "difference_count": len(differences),
        "common": matches[:10],
        "differences": differences[:10],
    }


# ============================================================
# VIEW LATEST RESULT
# ============================================================

@compatibility_bp.route("/compatibility/latest")
def view_latest():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth.login"))

    profile = PersonalityProfile.query.filter_by(
        user_id=user_id
    ).first()

    if not profile or not profile.compatibility_data:

        flash(
            "Please complete the couple compatibility test first.",
            "info",
        )

        return redirect(
            url_for(
                "compatibility.compatibility_test"
            )
        )

    try:
        result = json.loads(
            profile.compatibility_data
        )
    except Exception:
        flash(
            "Compatibility result could not be loaded.",
            "error",
        )

        return redirect(
            url_for(
                "compatibility.compatibility_test"
            )
        )

    return render_template(
        "compatibility_result.html",
        result=result,
    )

