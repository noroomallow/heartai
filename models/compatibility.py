from datetime import datetime

from models import db


class CompatibilityResult(db.Model):
    __tablename__ = "compatibility_results"

    id = db.Column(db.Integer, primary_key=True)
    relationship_id = db.Column(db.Integer, db.ForeignKey("relationships.id", ondelete="CASCADE"), nullable=False)

    personality_score = db.Column(db.Float, default=0.0)
    interests_score = db.Column(db.Float, default=0.0)
    values_score = db.Column(db.Float, default=0.0)
    communication_score = db.Column(db.Float, default=0.0)
    lifestyle_score = db.Column(db.Float, default=0.0)
    preference_score = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)

    category = db.Column(db.String(100), nullable=False, default="Needs Understanding")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    relationship = db.relationship("Relationship", back_populates="compatibility_results")
