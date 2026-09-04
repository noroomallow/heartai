import json
import os
import re
import time

from flask import current_app
from google import genai


class AIService:

    DEFAULT_MODEL = "gemini-3.7-flash"
    DEFAULT_FALLBACK_MODELS = [
        "gemini-3.6-flash",
        "gemini-3.5-flash-lite",
    ]

    @staticmethod
    def get_client():
        client = getattr(current_app, "client", None)
        if client is not None:
            return client

        api_key = (
            current_app.config.get("GEMINI_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        if not api_key or not api_key.strip():
            raise RuntimeError("GEMINI_API_KEY is missing. Add it to the .env file.")

        client = genai.Client(api_key=api_key.strip())
        current_app.client = client
        return client

    @staticmethod
    def get_models():
        primary = current_app.config.get("GEMINI_MODEL", AIService.DEFAULT_MODEL)
        fallbacks = current_app.config.get(
            "GEMINI_FALLBACK_MODELS", AIService.DEFAULT_FALLBACK_MODELS
        )
        if isinstance(fallbacks, str):
            fallbacks = [x.strip() for x in fallbacks.split(",") if x.strip()]
        return list(dict.fromkeys([primary] + list(fallbacks)))

    @staticmethod
    def _is_retryable_error(exc):
        text = f"{type(exc).__name__} {exc}".lower()
        return any(token in text for token in (
            "503", "unavailable", "429", "resource_exhausted",
            "500", "502", "504", "deadline", "temporarily", "high demand"
        ))

    @staticmethod
    def generate_text(prompt, system_instruction=None):
        client = AIService.get_client()
        full_prompt = (
            (system_instruction.strip() + "\n\n") if system_instruction else ""
        ) + prompt.strip()

        retries = max(0, int(current_app.config.get("GEMINI_RETRIES", 2)))
        base_delay = max(0.25, float(current_app.config.get("GEMINI_RETRY_BASE_SECONDS", 1.5)))
        errors = []

        for model_index, model in enumerate(AIService.get_models()):
            attempts = retries + 1
            for attempt in range(attempts):
                try:
                    response = client.models.generate_content(
                        model=model,
                        contents=full_prompt
                    )
                    text = getattr(response, "text", None)
                    if not text:
                        raise RuntimeError("Gemini returned an empty response.")
                    return text.strip()
                except Exception as exc:
                    errors.append(f"{model}: {type(exc).__name__}: {exc}")
                    print(f"\nGEMINI ERROR [{model}] attempt {attempt + 1}/{attempts}")
                    print(type(exc).__name__)
                    print(str(exc))
                    if not AIService._is_retryable_error(exc) or attempt >= retries:
                        break
                    delay = base_delay * (2 ** attempt)
                    print(f"Retrying Gemini in {delay:.1f}s...")
                    time.sleep(delay)

            if model_index < len(AIService.get_models()) - 1:
                print(f"Trying Gemini fallback model: {AIService.get_models()[model_index + 1]}")

        raise RuntimeError(
            "Gemini is temporarily unavailable after trying the configured models. "
            "Please try again shortly.\n" + "\n".join(errors[-6:])
        )

    @staticmethod
    def generate_json_response(prompt, system_instruction=None):
        text = AIService.generate_text(prompt, system_instruction).strip()
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        # Gemini may return either a JSON object or a JSON array.
        # Plans are commonly returned as an array of 30 task objects.
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        object_start, object_end = text.find("{"), text.rfind("}")
        array_start, array_end = text.find("["), text.rfind("]")
        candidates = []
        if object_start != -1 and object_end >= object_start:
            candidates.append(text[object_start:object_end + 1])
        if array_start != -1 and array_end >= array_start:
            candidates.append(text[array_start:array_end + 1])
        if not candidates:
            raise ValueError("Gemini did not return valid JSON.\n" + text)
        try:
            return json.loads(candidates[0])
        except json.JSONDecodeError:
            if len(candidates) > 1:
                try:
                    return json.loads(candidates[1])
                except json.JSONDecodeError:
                    pass
            raise ValueError("Gemini returned invalid JSON.")
        except json.JSONDecodeError as exc:
            print("JSON PARSE ERROR:", exc)
            print("GEMINI RESPONSE:", text)
            raise ValueError("Gemini returned invalid JSON.") from exc

    # =========================================================
    # WHATSAPP CHAT ANALYSIS
    #
    # IMPORTANT:
    # This accepts THREE arguments:
    #
    # analyze_whatsapp_chat(chat_text)
    # analyze_whatsapp_chat(chat_text, participants)
    # analyze_whatsapp_chat(chat_text, participants, stats)
    #
    # This fixes:
    # TypeError:
    # takes from 1 to 2 positional arguments
    # but 3 were given
    # =========================================================

    @staticmethod
    def analyze_whatsapp_chat(
        chat_text,
        participants=None,
        stats=None
    ):

        participants = participants or []
        stats = stats or {}

        # -----------------------------------------------------
        # Convert values safely
        # -----------------------------------------------------

        chat_text = str(chat_text or "").strip()

        if not chat_text:

            return {
                "positive_percentage": 0.0,
                "neutral_percentage": 100.0,
                "negative_percentage": 0.0,
                "communication_score": 50.0,
                "engagement_score": 50.0,
                "emotional_score": 50.0,
                "trust_score": 50.0,
                "compatibility_score": 50.0,
                "emotional_tone": "Neutral",
                "summary": "No conversation was provided.",
                "conversation_pattern": "",
                "relationship_signals": [],
                "strengths": [],
                "areas_to_improve": [],
                "suggestions": [],
                "detailed_analysis": "There was no conversation to analyze.",
                "analysis_text": "There was no conversation to analyze."
            }

        # -----------------------------------------------------
        # Limit extremely large conversations
        # -----------------------------------------------------

        if len(chat_text) > 30000:

            chat_text = chat_text[:30000]

        # -----------------------------------------------------
        # Participant information
        # -----------------------------------------------------

        participant_text = json.dumps(
            participants,
            ensure_ascii=False,
            default=str
        )

        # -----------------------------------------------------
        # Statistics information
        # -----------------------------------------------------

        statistics_text = json.dumps(
            stats,
            ensure_ascii=False,
            default=str
        )

        # =====================================================
        # GEMINI PROMPT
        # =====================================================

        prompt = f"""
You are HeartAI, an advanced AI relationship and communication
analysis system.

Analyze the following WhatsApp conversation carefully.

================ PARTICIPANTS ================

{participant_text}

================ STATISTICS ==================

{statistics_text}

================ CONVERSATION ================

{chat_text}

===============================================

The conversation may contain:

- English
- Tamil
- Tanglish
- Informal English
- Spelling mistakes
- Short messages
- Emojis
- Abbreviations
- Multiline messages
- Casual conversation
- Emotional messages

Understand the meaning from context.

Do NOT judge spelling or grammar.

Do NOT automatically assume romantic interest.

Do NOT diagnose mental health conditions.

Do NOT make unsupported claims.

Analyze only the communication patterns that are reasonably
supported by the conversation.

Evaluate the following:

1. Overall sentiment
2. Positive communication
3. Neutral communication
4. Negative communication
5. Communication quality
6. Emotional tone
7. Engagement
8. Mutual communication
9. Supportiveness
10. Respectfulness
11. Trust signals
12. Communication compatibility
13. Relationship signals
14. Strengths
15. Areas for improvement
16. Practical suggestions

IMPORTANT SCORING RULES:

sentiment_score:
0 = extremely negative
50 = neutral
100 = extremely positive

positive_percentage:
Percentage of positive communication.

neutral_percentage:
Percentage of neutral communication.

negative_percentage:
Percentage of negative communication.

communication_score:
0 = very poor communication
100 = excellent communication.

engagement_score:
0 = very low engagement
100 = very high engagement.

emotional_score:
0 = very low emotional connection
100 = very strong emotional connection.

trust_score:
0 = very weak trust signals
100 = very strong trust signals.

compatibility_score:
0 = very weak communication compatibility
100 = very strong communication compatibility.

The following three values MUST add up to exactly 100:

positive_percentage
neutral_percentage
negative_percentage

Be balanced.

Do not confuse:

- friendship with romance
- politeness with romantic interest
- disagreement with a toxic relationship
- short replies with lack of care
- emojis with definite emotions

Consider the entire conversation rather than isolated messages.

Examples of Tanglish that may appear:

"Enaku 2 naal class irunchu"

"Adhunala dha vara mudila"

"Na faraz kita sonen"

"Vara mudiyadhu apdinu"

"Thappa eduthukadha"

"varanum nu dha irundhen"

Understand such messages contextually.

Return ONLY valid JSON.

Do NOT return Markdown.

Do NOT return ```json.

Do NOT add text before or after the JSON.

Use EXACTLY this structure:

{{
    "sentiment_score": 0,
    "positive_percentage": 0,
    "neutral_percentage": 0,
    "negative_percentage": 0,
    "communication_score": 0,
    "engagement_score": 0,
    "emotional_score": 0,
    "trust_score": 0,
    "compatibility_score": 0,
    "emotional_tone": "",
    "summary": "",
    "conversation_pattern": "",
    "relationship_signals": [],
    "strengths": [],
    "areas_to_improve": [],
    "suggestions": [],
    "detailed_analysis": ""
}}
"""

        # =====================================================
        # CALL GEMINI
        # =====================================================

        try:

            result = AIService.generate_json_response(prompt)

            # -------------------------------------------------
            # Safe numeric conversion
            # -------------------------------------------------

            def number(value, default=0):

                try:
                    return max(
                        0.0,
                        min(100.0, float(value))
                    )

                except (TypeError, ValueError):

                    return float(default)

            positive = number(
                result.get("positive_percentage"),
                33
            )

            neutral = number(
                result.get("neutral_percentage"),
                34
            )

            negative = number(
                result.get("negative_percentage"),
                33
            )

            # -------------------------------------------------
            # Normalize percentages
            # -------------------------------------------------

            total = positive + neutral + negative

            if total <= 0:

                positive = 33.0
                neutral = 34.0
                negative = 33.0

            else:

                positive = (positive / total) * 100
                neutral = (neutral / total) * 100
                negative = 100 - positive - neutral

            # -------------------------------------------------
            # Get arrays safely
            # -------------------------------------------------

            relationship_signals = result.get(
                "relationship_signals",
                []
            )

            strengths = result.get(
                "strengths",
                []
            )

            areas_to_improve = result.get(
                "areas_to_improve",
                []
            )

            suggestions = result.get(
                "suggestions",
                []
            )

            if not isinstance(
                relationship_signals,
                list
            ):
                relationship_signals = [
                    str(relationship_signals)
                ]

            if not isinstance(strengths, list):
                strengths = [str(strengths)]

            if not isinstance(
                areas_to_improve,
                list
            ):
                areas_to_improve = [
                    str(areas_to_improve)
                ]

            if not isinstance(suggestions, list):
                suggestions = [str(suggestions)]

            # -------------------------------------------------
            # Final result
            # -------------------------------------------------

            detailed_analysis = str(
                result.get(
                    "detailed_analysis",
                    result.get(
                        "summary",
                        ""
                    )
                )
            )

            final_result = {

                "sentiment_score": number(
                    result.get(
                        "sentiment_score",
                        50
                    ),
                    50
                ),

                "positive_percentage": round(
                    positive,
                    2
                ),

                "neutral_percentage": round(
                    neutral,
                    2
                ),

                "negative_percentage": round(
                    negative,
                    2
                ),

                "communication_score": number(
                    result.get(
                        "communication_score",
                        50
                    ),
                    50
                ),

                "engagement_score": number(
                    result.get(
                        "engagement_score",
                        50
                    ),
                    50
                ),

                "emotional_score": number(
                    result.get(
                        "emotional_score",
                        50
                    ),
                    50
                ),

                "trust_score": number(
                    result.get(
                        "trust_score",
                        50
                    ),
                    50
                ),

                "compatibility_score": number(
                    result.get(
                        "compatibility_score",
                        50
                    ),
                    50
                ),

                "emotional_tone": str(
                    result.get(
                        "emotional_tone",
                        "Neutral"
                    )
                ),

                "summary": str(
                    result.get(
                        "summary",
                        "No summary was returned."
                    )
                ),

                "conversation_pattern": str(
                    result.get(
                        "conversation_pattern",
                        ""
                    )
                ),

                "relationship_signals":
                    relationship_signals,

                "strengths":
                    strengths,

                "areas_to_improve":
                    areas_to_improve,

                "suggestions":
                    suggestions,

                "detailed_analysis":
                    detailed_analysis,

                # Backward compatibility
                "analysis_text":
                    detailed_analysis
            }

            print(
                "\n========== HEARTAI CHAT ANALYSIS =========="
            )

            print(
                json.dumps(
                    final_result,
                    indent=2,
                    ensure_ascii=False
                )
            )

            print(
                "===========================================\n"
            )

            return final_result

        except Exception as e:

            print(
                "\n========== CHAT ANALYSIS ERROR =========="
            )

            print(
                type(e).__name__
            )

            print(
                str(e)
            )

            print(
                "=========================================\n"
            )

            # -------------------------------------------------
            # Safe fallback
            # -------------------------------------------------

            return {

                "sentiment_score": 50.0,

                "positive_percentage": 33.0,

                "neutral_percentage": 34.0,

                "negative_percentage": 33.0,

                "communication_score": 50.0,

                "engagement_score": 50.0,

                "emotional_score": 50.0,

                "trust_score": 50.0,

                "compatibility_score": 50.0,

                "emotional_tone": "Unavailable",

                "summary":
                    "AI analysis is temporarily unavailable.",

                "conversation_pattern": "",

                "relationship_signals": [],

                "strengths": [],

                "areas_to_improve": [],

                "suggestions": [
                    "Please try the analysis again."
                ],

                "detailed_analysis":
                    "Gemini analysis failed. "
                    "Please check the Flask terminal for the "
                    "exact error.",

                "analysis_text":
                    "Gemini analysis failed. "
                    "Please try again."
            }

    # =========================================================
    # BACKWARD COMPATIBILITY
    # =========================================================

    @staticmethod
    def analyze_chat(chat_text):

        return AIService.analyze_whatsapp_chat(
            chat_text
        )

    # =========================================================
    # AI RELATIONSHIP COACH
    # =========================================================

    @staticmethod
    def generate_coach_reply(
        message,
        context=None
    ):

        context = context or {}

        prompt = f"""
You are HeartAI Relationship Coach.

User's question:

{message}

Relationship context:

{json.dumps(
    context,
    ensure_ascii=False,
    default=str
)}

Give a helpful relationship coaching response.

Requirements:

1. Be empathetic and practical.
2. Do not pretend to know facts that are unavailable.
3. Do not diagnose mental health conditions.
4. Do not encourage manipulation, stalking,
   harassment or controlling behavior.
5. Give practical communication advice.
6. If appropriate, suggest a message the user can send.
7. Keep the answer under 250 words.
8. Do not mention API keys, programming
   or internal systems.
"""

        try:

            return AIService.generate_text(
                prompt
            )

        except Exception as e:

            print(
                "Coach error:",
                type(e).__name__,
                str(e)
            )

            return (
                "I'm temporarily unable to connect "
                "to the AI coach. Please try again "
                "in a moment."
            )

    # =========================================================
    # PERSONALITY ANALYSIS
    # =========================================================

    @staticmethod
    def analyze_personality(profile_data):

        prompt = f"""
You are HeartAI.

Analyze this personality profile:

{json.dumps(
    profile_data,
    ensure_ascii=False,
    default=str
)}

Provide a clear and friendly
relationship-focused interpretation.

Cover:

- Personality overview
- Communication style
- Emotional openness
- Conflict style
- Trust level
- Social preference
- Relationship expectations
- Strengths
- Possible challenges
- Practical relationship advice

Do not diagnose medical or psychological conditions.

Keep the explanation practical,
balanced and easy to understand.
"""

        try:

            return AIService.generate_text(
                prompt
            )

        except Exception as e:

            print(
                "Personality AI error:",
                type(e).__name__,
                str(e)
            )

            return (
                "AI personality explanation is "
                "temporarily unavailable."
            )

