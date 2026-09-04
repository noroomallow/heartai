from datetime import datetime

from models import db


class ChatAnalysis(db.Model):
    __tablename__ = "chat_analyses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    relationship_id = db.Column(db.Integer, db.ForeignKey("relationships.id", ondelete="SET NULL"), nullable=True)

    participants = db.Column(db.Text, nullable=True)
    total_messages = db.Column(db.Integer, default=0)
    participant_statistics = db.Column(db.Text, nullable=True)

    positive_percentage = db.Column(db.Float, default=0.0)
    neutral_percentage = db.Column(db.Float, default=0.0)
    negative_percentage = db.Column(db.Float, default=0.0)
    communication_score = db.Column(db.Float, default=0.0)
    engagement_score = db.Column(db.Float, default=0.0)
    emotional_score = db.Column(db.Float, default=0.0)
    trust_score = db.Column(db.Float, default=0.0)
    compatibility_score = db.Column(db.Float, default=0.0)

    emotional_tone = db.Column(db.String(100), default="Neutral")
    ai_summary = db.Column(db.Text, nullable=True)
    ai_analysis_json = db.Column(db.Text, nullable=True)

    chat_text = db.Column(db.Text, nullable=False)
    analysis = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="chat_analyses")
    relationship = db.relationship("Relationship", back_populates="chat_analyses")

    def __repr__(self):
        return f"<ChatAnalysis {self.id}>"
