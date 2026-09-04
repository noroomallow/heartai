import json
from services.ai_service import AIService


class RecommendationService:
    @staticmethod
    def generate_fallback_report(scores, partner_name):
        overall = scores.get("overall_score", 70.0)
        return {
            "summary": f"Your assessment with {partner_name} indicates an overall relationship score of {overall}%. The score highlights areas to celebrate and areas where small, consistent habits may strengthen the bond.",
            "compatibility_explanation": "The assessment combines the completed relationship tests. It is a structured reflection tool, not a prediction of relationship success.",
            "strengths": [
                "You have taken time to understand the relationship intentionally.",
                "There are opportunities to build positive routines through quality time and communication.",
            ],
            "challenges": [
                "Different preferences may require clearer conversations and compromise.",
                "Busy schedules can reduce consistent quality time if it is not planned.",
            ],
            "recommendations": [
                "Schedule one distraction-free check-in each week.",
                "Plan enjoyable shared activities instead of making every conversation problem-focused.",
                "Use specific appreciation and respectful 'I feel' statements during difficult conversations.",
            ],
            "communication_tips": [
                "Listen to understand before offering a solution.",
                "Pause and return to difficult conversations when both people are calmer.",
            ],
            "date_ideas": [
                "Movie and homemade snack night.",
                "Coffee and evening walk.",
                "Cook a new recipe together.",
                "Choose a new outfit or accessory together and finish with dessert.",
                "Low-cost photo walk and memory challenge.",
            ],
            "next_steps": [
                "Complete the next relationship check-in after the 30-day plan.",
                "Continue the three activities that felt most natural to both partners.",
            ],
        }

    @classmethod
    def get_full_report(cls, scores, p1_name, p2_name, extra_context=None):
        extra_context = extra_context or {}
        prompt = f"""
You are HeartAI, a relationship reflection and bonding assistant.
Create professional, warm, practical content for a couple's final relationship report.
Couple: {p1_name} and {p2_name}
Scores: {json.dumps(scores, ensure_ascii=False, default=str)}
Additional context: {json.dumps(extra_context, ensure_ascii=False, default=str)}

Return ONLY a JSON object with these keys:
summary, compatibility_explanation, strengths, challenges, recommendations,
communication_tips, date_ideas, next_steps.
Each list must contain useful, specific items. Make recommendations practical and mutual.
Include enjoyable bonding ideas such as dates, movies, cooking, walks, small surprises,
style/outfit shopping within a reasonable budget, hobbies and memory-making where appropriate.
Do not present astrology as scientific or predictive. Do not claim certainty about the future.
Do not diagnose or act as a therapist. Do not encourage manipulation, control, stalking,
coercion or abuse. If the context suggests danger, recommend trusted/professional support.
"""
        try:
            result = AIService.generate_json_response(prompt)
            if result and isinstance(result, dict):
                fallback = cls.generate_fallback_report(scores, p2_name)
                for key, value in fallback.items():
                    if not result.get(key):
                        result[key] = value
                return result
        except Exception as exc:
            print("AI report fallback:", type(exc).__name__, str(exc))
        return cls.generate_fallback_report(scores, p2_name)
