import json
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from models import db
from models.astrology import AstrologyProfile, AstrologyReading
from services.astrology_service import AstrologyService

astrology_bp = Blueprint("astrology", __name__)


def _person(prefix=""):
    return {"full_name":request.form.get(prefix+"full_name","").strip(),"last_name":request.form.get(prefix+"last_name","").strip(),"birth_date":request.form.get(prefix+"birth_date","").strip(),"birth_time":request.form.get(prefix+"birth_time","").strip(),"birth_place":request.form.get(prefix+"birth_place","").strip()}


def _normalise(p):
    if p["last_name"]:
        p["full_name"] = f'{p["full_name"]} {p["last_name"]}'.strip()
    return p


def _save_profile(user_id, person, data):
    profile = AstrologyProfile.query.filter_by(user_id=user_id).first() or AstrologyProfile(user_id=user_id)
    profile.person_name = data.get("name", person["full_name"])
    profile.birth_date = person["birth_date"]
    profile.birth_time = person["birth_time"]
    profile.birth_place = person["birth_place"]
    profile.zodiac_sign = data.get("zodiac_sign", "Unknown")
    profile.moon_sign = data.get("rasi", "")
    profile.nakshatra = data.get("nakshatra", "")
    profile.personality_summary = data.get("personality", "")
    profile.career_summary = data.get("career", "")
    profile.relationship_summary = data.get("love_relationship", "")
    profile.strengths = json.dumps(data.get("strengths", []), ensure_ascii=False)
    profile.challenges = json.dumps(data.get("challenges", []), ensure_ascii=False)
    profile.ai_analysis = json.dumps(data, ensure_ascii=False)
    db.session.add(profile); db.session.flush()
    return profile


@astrology_bp.route("/astrology", methods=["GET","POST"])
def astrology_view():
    user_id = session.get("user_id")
    if not user_id: return redirect(url_for("auth.login"))
    if request.method == "GET":
        latest = AstrologyReading.query.filter_by(user_id=user_id).order_by(AstrologyReading.id.desc()).first()
        return render_template("astrology.html", reading=latest, person1_data=latest.get_person1_data() if latest else None, person2_data=latest.get_person2_data() if latest else None, combined_data=latest.get_combined_data() if latest else None)

    mode = request.form.get("mode","single").lower()
    person1 = _normalise(_person())
    ok, err = AstrologyService.validate_person(person1)
    if not ok:
        flash(err,"danger"); return redirect(url_for("astrology.astrology_view"))

    if mode == "single":
        r = AstrologyService.generate_person_reading(person1)
        if not r["success"]:
            flash(r["error"],"danger"); return redirect(url_for("astrology.astrology_view"))
        data = r["data"]; profile = _save_profile(user_id,person1,data)
        db.session.add(AstrologyReading(user_id=user_id,profile_id=profile.id,mode="single",person1_name=data.get("name",person1["full_name"]),person1_data=json.dumps(data,ensure_ascii=False)))
        db.session.commit(); flash("Astrology analysis generated successfully.","success")
        return redirect(url_for("astrology.astrology_view"))

    if mode == "couple":
        person2 = _normalise(_person("partner_"))
        ok, err = AstrologyService.validate_person(person2)
        if not ok:
            flash(f"Partner: {err}","danger"); return redirect(url_for("astrology.astrology_view"))
        r1 = AstrologyService.generate_person_reading(person1); r2 = AstrologyService.generate_person_reading(person2)
        if not r1["success"]: flash(r1["error"],"danger"); return redirect(url_for("astrology.astrology_view"))
        if not r2["success"]: flash(r2["error"],"danger"); return redirect(url_for("astrology.astrology_view"))
        combined = AstrologyService.generate_couple_reading(person1,person2,r1["data"],r2["data"])
        if not combined["success"]: flash(combined["error"],"danger"); return redirect(url_for("astrology.astrology_view"))
        profile = _save_profile(user_id,person1,r1["data"])
        db.session.add(AstrologyReading(user_id=user_id,profile_id=profile.id,mode="couple",person1_name=r1["data"]["name"],person2_name=r2["data"]["name"],person1_data=json.dumps(r1["data"],ensure_ascii=False),person2_data=json.dumps(r2["data"],ensure_ascii=False),combined_data=json.dumps(combined["data"],ensure_ascii=False)))
        db.session.commit(); flash("Couple astrology analysis generated successfully.","success")
        return redirect(url_for("astrology.astrology_view"))
    flash("Invalid astrology mode.","danger")
    return redirect(url_for("astrology.astrology_view"))
