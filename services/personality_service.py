
"""
HeartAI Personality Test Scoring Engine

50 questions
1-5 scoring system
Final score: 0-100

Python calculates the numerical score.
Gemini is only used for explanation.
"""


class PersonalityService:

    # ==========================================================
    # QUESTION → DIMENSION
    # ==========================================================

    QUESTION_DIMENSIONS = {

        1: "confidence",
        2: "relationship",
        3: "self_awareness",
        4: "social",
        5: "self_awareness",

        6: "trust",
        7: "social",
        8: "confidence",
        9: "decision_making",
        10: "emotional_stability",

        11: "emotional_stability",
        12: "confidence",
        13: "self_awareness",
        14: "empathy",
        15: "personality",

        16: "emotional_stability",
        17: "forgiveness",
        18: "emotional_stability",
        19: "emotional_expression",
        20: "affection",

        21: "self_awareness",
        22: "overthinking",
        23: "stress_management",
        24: "emotional_stability",
        25: "emotional_support",

        26: "empathy",
        27: "respect",
        28: "respect",
        29: "care",
        30: "empathy",

        31: "empathy",
        32: "values",
        33: "communication",
        34: "emotional_expression",
        35: "communication",

        36: "communication",
        37: "communication",
        38: "self_awareness",
        39: "relationship",
        40: "independence",

        41: "affection",
        42: "conflict_handling",
        43: "honesty",
        44: "jealousy_management",
        45: "relationship",

        46: "relationship",
        47: "conflict_handling",
        48: "trust",
        49: "boundaries",
        50: "relationship",
    }

    # ==========================================================
    # NEGATIVE / REVERSE QUESTIONS
    # ==========================================================

    REVERSE_QUESTIONS = {
        19,
        22,
        24,
        44,
        47,
        48,
    }

    # ==========================================================
    # DIMENSION NAMES
    # ==========================================================

    DIMENSION_LABELS = {

        "confidence": "Confidence",
        "relationship": "Relationship Orientation",
        "self_awareness": "Self Awareness",
        "social": "Social Behaviour",
        "trust": "Trust",
        "decision_making": "Decision Making",
        "emotional_stability": "Emotional Stability",
        "empathy": "Empathy",
        "personality": "Personality",
        "forgiveness": "Forgiveness",
        "emotional_expression": "Emotional Expression",
        "affection": "Affection",
        "overthinking": "Overthinking",
        "stress_management": "Stress Management",
        "emotional_support": "Emotional Support",
        "respect": "Respect",
        "care": "Care",
        "values": "Values",
        "communication": "Communication",
        "independence": "Independence",
        "conflict_handling": "Conflict Handling",
        "honesty": "Honesty",
        "jealousy_management": "Jealousy Management",
        "boundaries": "Healthy Boundaries",
    }

    # ==========================================================
    # CONVERT ANSWER
    # ==========================================================

    @staticmethod
    def answer_to_score(answer):

        try:

            score = float(answer)

            if score < 1:
                return 1.0

            if score > 5:
                return 5.0

            return score

        except (
            ValueError,
            TypeError
        ):

            return 3.0

    # ==========================================================
    # NORMALIZE 1-5 → 0-100
    # ==========================================================

    @classmethod
    def normalize_score(
        cls,
        question_number,
        score
    ):

        score = cls.answer_to_score(score)

        if question_number in cls.REVERSE_QUESTIONS:

            score = 6 - score

        return round(
            ((score - 1) / 4) * 100,
            2
        )

    # ==========================================================
    # DIMENSION CALCULATION
    # ==========================================================

    @classmethod
    def calculate_dimensions(
        cls,
        answers
    ):

        totals = {}
        counts = {}

        for question_number, dimension in cls.QUESTION_DIMENSIONS.items():

            answer = answers.get(
                str(question_number)
            )

            if answer is None:
                continue

            score = cls.normalize_score(
                question_number,
                answer
            )

            totals[dimension] = (
                totals.get(dimension, 0)
                + score
            )

            counts[dimension] = (
                counts.get(dimension, 0)
                + 1
            )

        dimensions = {}

        for dimension in totals:

            dimensions[dimension] = round(
                totals[dimension]
                / counts[dimension],
                2
            )

        return dimensions

    # ==========================================================
    # OVERALL SCORE
    # ==========================================================

    @staticmethod
    def calculate_overall_score(
        dimensions
    ):

        if not dimensions:
            return 0

        return round(
            sum(dimensions.values())
            / len(dimensions),
            2
        )

    # ==========================================================
    # RELATIONSHIP SCORE
    # ==========================================================

    @staticmethod
    def calculate_relationship_score(
        dimensions
    ):

        relationship_dimensions = [

            "relationship",
            "trust",
            "communication",
            "empathy",
            "respect",
            "affection",
            "conflict_handling",
            "honesty",
            "boundaries",
            "jealousy_management",
        ]

        scores = [
            dimensions[x]
            for x in relationship_dimensions
            if x in dimensions
        ]

        if not scores:
            return 0

        return round(
            sum(scores) / len(scores),
            2
        )

    # ==========================================================
    # PERSONALITY TYPE
    # ==========================================================

    @staticmethod
    def get_personality_type(
        dimensions
    ):

        emotional = dimensions.get(
            "emotional_stability",
            50
        )

        empathy = dimensions.get(
            "empathy",
            50
        )

        communication = dimensions.get(
            "communication",
            50
        )

        confidence = dimensions.get(
            "confidence",
            50
        )

        relationship = dimensions.get(
            "relationship",
            50
        )

        independence = dimensions.get(
            "independence",
            50
        )

        if (
            emotional >= 75
            and empathy >= 70
            and communication >= 70
        ):
            return "Emotionally Balanced Communicator"

        if (
            empathy >= 75
            and relationship >= 70
        ):
            return "Caring & Supportive"

        if (
            confidence >= 75
            and independence >= 70
        ):
            return "Independent & Confident"

        if (
            communication >= 75
            and confidence >= 65
        ):
            return "Expressive & Social"

        if (
            relationship >= 75
            and empathy >= 65
        ):
            return "Deeply Relationship-Oriented"

        if (
            emotional < 45
            and communication < 50
        ):
            return "Emotionally Reserved"

        return "Balanced Personality"

    # ==========================================================
    # RELATIONSHIP CATEGORY
    # ==========================================================

    @staticmethod
    def get_relationship_category(score):

        if score >= 85:
            return "Excellent Relationship Potential"

        if score >= 70:
            return "Strong Relationship Potential"

        if score >= 55:
            return "Good Relationship Potential"

        if score >= 40:
            return "Needs Emotional Growth"

        return "Needs Significant Improvement"

    # ==========================================================
    # STRENGTHS
    # ==========================================================

    @classmethod
    def get_strengths(
        cls,
        dimensions
    ):

        strengths = []

        for key, score in dimensions.items():

            if score >= 75:

                strengths.append(
                    cls.DIMENSION_LABELS.get(
                        key,
                        key.replace(
                            "_",
                            " "
                        ).title()
                    )
                )

        if not strengths:

            strengths.append(
                "Balanced personality qualities"
            )

        return strengths[:6]

    # ==========================================================
    # IMPROVEMENT AREAS
    # ==========================================================

    @classmethod
    def get_improvements(
        cls,
        dimensions
    ):

        improvements = []

        for key, score in dimensions.items():

            if score < 45:

                improvements.append(
                    cls.DIMENSION_LABELS.get(
                        key,
                        key.replace(
                            "_",
                            " "
                        ).title()
                    )
                )

        if not improvements:

            improvements.append(
                "Continue developing your existing strengths."
            )

        return improvements[:6]

    # ==========================================================
    # FINAL RESULT
    # ==========================================================

    @classmethod
    def analyze(
        cls,
        answers
    ):

        dimensions = cls.calculate_dimensions(
            answers
        )

        overall_score = cls.calculate_overall_score(
            dimensions
        )

        relationship_score = cls.calculate_relationship_score(
            dimensions
        )

        personality_type = cls.get_personality_type(
            dimensions
        )

        relationship_category = (
            cls.get_relationship_category(
                relationship_score
            )
        )

        strengths = cls.get_strengths(
            dimensions
        )

        improvements = cls.get_improvements(
            dimensions
        )

        return {

            "overall_score":
                overall_score,

            "personality_type":
                personality_type,

            "relationship_score":
                relationship_score,

            "relationship_category":
                relationship_category,

            "dimensions":
                dimensions,

            "strengths":
                strengths,

            "areas_for_improvement":
                improvements,

            "total_questions":
                50,

            "answered_questions":
                len(answers),
        }

