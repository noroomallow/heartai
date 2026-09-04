from textblob import TextBlob

class SentimentService:
    @staticmethod
    def analyze_chat_text(text):
        if not text or not text.strip():
            return {
                "sentiment_score": 50.0,
                "positive_percentage": 33.33,
                "neutral_percentage": 33.34,
                "negative_percentage": 33.33,
                "communication_score": 50.0,
                "emotional_tone": "Neutral",
                "analysis_text": "Detected language patterns suggest a balanced interaction with stable neutral pacing."
            }

        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1.0 to 1.0

        sentences = blob.sentences
        pos, neu, neg = 0, 0, 0
        total = len(sentences) if len(sentences) > 0 else 1

        for sentence in sentences:
            p = sentence.sentiment.polarity
            if p > 0.1:
                pos += 1
            elif p < -0.1:
                neg += 1
            else:
                neu += 1

        pos_pct = round((pos / total) * 100, 2)
        neu_pct = round((neu / total) * 100, 2)
        neg_pct = round((neg / total) * 100, 2)

        sentiment_score = round(((polarity + 1) / 2) * 100, 2)
        comm_score = round(max(0.0, min(100.0, (pos_pct * 0.7) + (neu_pct * 0.3) - (neg_pct * 0.5))), 2)

        if polarity > 0.35:
            tone = "Warm & Enthusiastic"
        elif polarity > 0.05:
            tone = "Constructive & Friendly"
        elif polarity > -0.1:
            tone = "Neutral & Direct"
        elif polarity > -0.35:
            tone = "Guarded or Distant"
        else:
            tone = "Tense or Frustrated"

        analysis_summary = f"Detected language patterns suggest a {tone.lower()} conversational tone. Positive expression constitutes {pos_pct}%, with neutral context at {neu_pct}%."

        return {
            "sentiment_score": sentiment_score,
            "positive_percentage": pos_pct,
            "neutral_percentage": neu_pct,
            "negative_percentage": neg_pct,
            "communication_score": comm_score,
            "emotional_tone": tone,
            "analysis_text": analysis_summary
        }