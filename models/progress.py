from datetime import datetime

from models import db


class ProgressTracking(db.Model):
    __tablename__ = "progress_tracking"

    id = db.Column(db.Integer, primary_key=True)
    relationship_id = db.Column(db.Integer, db.ForeignKey("relationships.id", ondelete="CASCADE"), nullable=False)
    communication_score = db.Column(db.Float, default=0.0)
    emotional_score = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
