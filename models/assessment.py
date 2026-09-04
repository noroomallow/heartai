from datetime import datetime
from models import db


class AssessmentSnapshot(db.Model):
    __tablename__ = "assessment_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    relationship_id = db.Column(db.Integer, db.ForeignKey("relationships.id", ondelete="CASCADE"), nullable=True)
    overall_score = db.Column(db.Float, default=0.0, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    personality_score = db.Column(db.Float, default=0.0)
    compatibility_score = db.Column(db.Float, default=0.0)
    chat_score = db.Column(db.Float, default=0.0)
    emotional_score = db.Column(db.Float, default=0.0)
    trust_score = db.Column(db.Float, default=0.0)
    tests_completed = db.Column(db.Integer, default=0)
    score_breakdown = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
