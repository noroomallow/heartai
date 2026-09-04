class CompatibilityEngine:
    @staticmethod
    def calculate_dimension_difference(val1, val2):
        return max(0.0, 100.0 - abs(float(val1) - float(val2)))

    @staticmethod
    def compute_text_similarity(text1, text2):
        if not text1 or not text2:
            return 50.0
        set1 = set(text1.lower().replace(',', ' ').split())
        set2 = set(text2.lower().replace(',', ' ').split())
        if not set1 or not set2:
            return 50.0
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        jaccard = len(intersection) / len(union)
        return round(40.0 + (jaccard * 60.0), 2)

    @classmethod
    def calculate_compatibility(cls, profile1, profile2):
        p1 = profile1
        p2 = profile2

        personality_score = cls.calculate_dimension_difference(p1.conflict_style, p2.conflict_style)
        interests_score = cls.compute_text_similarity(p1.interests_text, p2.interests_text)
        values_score = cls.calculate_dimension_difference(p1.trust_level, p2.trust_level)
        communication_score = cls.calculate_dimension_difference(p1.communication_style, p2.communication_style)
        lifestyle_score = cls.calculate_dimension_difference(p1.social_preference, p2.social_preference)
        preference_score = cls.calculate_dimension_difference(p1.relationship_expectation, p2.relationship_expectation)

        weighted_score = (
            (personality_score * 0.25) +
            (interests_score * 0.15) +
            (values_score * 0.20) +
            (communication_score * 0.20) +
            (lifestyle_score * 0.10) +
            (preference_score * 0.10)
        )

        overall_score = round(max(0.0, min(100.0, weighted_score)), 2)

        if overall_score >= 80.0:
            category = "HIGH COMPATIBILITY"
        elif overall_score >= 60.0:
            category = "MODERATE COMPATIBILITY"
        else:
            category = "NEEDS ATTENTION"

        return {
            "personality_score": round(personality_score, 2),
            "interests_score": round(interests_score, 2),
            "values_score": round(values_score, 2),
            "communication_score": round(communication_score, 2),
            "lifestyle_score": round(lifestyle_score, 2),
            "preference_score": round(preference_score, 2),
            "overall_score": overall_score,
            "category": category
        }