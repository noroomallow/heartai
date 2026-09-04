import json
import os
import re
from datetime import datetime
from flask import current_app
from google import genai


class AstrologyService:
    MODELS = [os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), "gemini-3.7-flash"]

    @classmethod
    def get_client(cls):
        try:
            client = getattr(current_app, "client", None)
            if client:
                return client
        except RuntimeError:
            pass
        key = os.getenv("GEMINI_API_KEY")
        return genai.Client(api_key=key) if key else None

    @staticmethod
    def _json(text):
        text = re.sub(r"^```(?:json)?\s*", "", (text or "").strip(), flags=re.I)
        text = re.sub(r"\s*```$", "", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find("{"), text.rfind("}")
            if start >= 0 and end > start:
                return json.loads(text[start:end + 1])
            raise

    @staticmethod
    def get_zodiac_sign(day, month):
        dates = [(1,20,"Capricorn","Aquarius"),(2,19,"Aquarius","Pisces"),(3,21,"Pisces","Aries"),(4,20,"Aries","Taurus"),(5,21,"Taurus","Gemini"),(6,21,"Gemini","Cancer"),(7,23,"Cancer","Leo"),(8,23,"Leo","Virgo"),(9,23,"Virgo","Libra"),(10,23,"Libra","Scorpio"),(11,22,"Scorpio","Sagittarius"),(12,22,"Sagittarius","Capricorn")]
        for m, split, first, second in dates:
            if month == m:
                return first if day < split else second
        return "Unknown"

    @classmethod
    def determine_sign_from_date(cls, date_str):
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return cls.get_zodiac_sign(dt.day, dt.month)
        except (TypeError, ValueError):
            return "Unknown"

    @staticmethod
    def validate_person(person):
        for field in ("full_name", "birth_date", "birth_time", "birth_place"):
            if not str(person.get(field, "")).strip():
                return False, f"{field.replace('_', ' ').title()} is required."
        try:
            datetime.strptime(person["birth_date"], "%Y-%m-%d")
        except (TypeError, ValueError):
            return False, "Birth Date must use YYYY-MM-DD format."
        return True, ""

    @classmethod
    def _generate(cls, prompt):
        client = cls.get_client()
        if not client:
            raise RuntimeError("Gemini API is not configured. Add GEMINI_API_KEY to .env.")
        last = None
        for model in dict.fromkeys(cls.MODELS):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={"response_mime_type": "application/json", "temperature": 0.7},
                )
                text = getattr(response, "text", None)
                if text:
                    return cls._json(text)
            except Exception as exc:
                last = exc
                print(f"Astrology model {model} failed: {type(exc).__name__}: {exc}")
        raise last or RuntimeError("No astrology response returned.")

    @classmethod
    def generate_person_reading(cls, person):
        full_name = " ".join(x for x in [person.get("full_name", "").strip(), person.get("last_name", "").strip()] if x)
        zodiac = cls.determine_sign_from_date(person["birth_date"])
        prompt = f"""
You are HeartAI Astrology Insight Engine. Create a detailed traditional astrology-style
interpretation for entertainment and personal reflection. Do not present astrology as
scientifically proven. Do not guarantee future events or make medical/psychological diagnoses.
Do not invent exact planetary degrees. If Moon sign/Rasi or Nakshatra cannot be accurately
calculated from the supplied information, clearly label them as AI-based traditional estimates.

Name: {full_name}
Birth date: {person['birth_date']}
Birth time: {person['birth_time']}
Birth place: {person['birth_place']}
Sun zodiac: {zodiac}

Return JSON with these fields:
{{
 "name":"", "birth_date":"", "birth_time":"", "birth_place":"", "zodiac_sign":"",
 "rasi":"", "nakshatra":"", "nakshatra_pada":"", "character":"", "personality":"",
 "emotional_nature":"", "communication_style":"", "strengths":[], "challenges":[],
 "career":"", "suitable_careers":[], "work_style":"", "financial_tendencies":"",
 "love_relationship":"", "family_social_nature":"", "growth_areas":[],
 "important_life_themes":[], "summary":"", "calculation_note":"",
 "disclaimer":"Astrology-based interpretation for entertainment and personal reflection only."
}}
Make every text field descriptive rather than one sentence.
"""
        try:
            result = cls._generate(prompt)
            result.update({"name": full_name, "birth_date": person["birth_date"], "birth_time": person["birth_time"], "birth_place": person["birth_place"], "zodiac_sign": zodiac})
            return {"success": True, "data": result}
        except Exception as exc:
            print(f"Person astrology error: {type(exc).__name__}: {exc}")
            return {"success": False, "error": str(exc)}

    @classmethod
    def generate_couple_reading(cls, person1, person2, person1_result, person2_result):
        prompt = f"""
You are HeartAI Couple Astrology Insight Engine. Give a detailed traditional astrology-style
relationship interpretation for entertainment and reflection only. Do not claim scientific
certainty, guaranteed marriage/separation, future events, or hidden feelings.

PERSON 1:
{json.dumps(person1_result, ensure_ascii=False)}

PERSON 2:
{json.dumps(person2_result, ensure_ascii=False)}

Return JSON with detailed values for:
"couple_summary","common_character","personality_connection","differences",
"emotional_compatibility","communication_compatibility","love_relationship",
"mutual_attraction","understanding_support","conflict_tendencies","shared_strengths",
"possible_challenges","career_life_goal_harmony","family_social_compatibility",
"how_they_complement","areas_for_understanding","relationship_advice",
"overall_interpretation","disclaimer".
Lists must contain practical, specific points.
"""
        try:
            return {"success": True, "data": cls._generate(prompt)}
        except Exception as exc:
            print(f"Couple astrology error: {type(exc).__name__}: {exc}")
            return {"success": False, "error": str(exc)}

    @staticmethod
    def evaluate_astrology_compatibility(sign1, sign2):
        elements = {"Fire":["Aries","Leo","Sagittarius"],"Earth":["Taurus","Virgo","Capricorn"],"Air":["Gemini","Libra","Aquarius"],"Water":["Cancer","Scorpio","Pisces"]}
        def el(sign):
            for e, signs in elements.items():
                if sign in signs: return e
            return "Unknown"
        a,b=el(sign1),el(sign2)
        if a == b: return f"Both signs belong to the {a} element, which can create a familiar and naturally understandable dynamic."
        if {a,b} <= {"Fire","Air"} or {a,b} <= {"Earth","Water"}: return f"The {a} and {b} elements are traditionally viewed as complementary, suggesting areas of mutual support."
        return f"The {a} and {b} elements may bring different styles. Open communication and flexibility can help balance those differences."
