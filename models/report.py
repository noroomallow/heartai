from datetime import datetime

from models import db


class AIReport(db.Model):
    __tablename__ = "ai_reports"

    id = db.Column(db.Integer, primary_key=True)
    relationship_id = db.Column(db.Integer, db.ForeignKey("relationships.id", ondelete="CASCADE"), nullable=False)
    report_type = db.Column(db.String(50), default="full_compatibility", nullable=False)
    report_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
