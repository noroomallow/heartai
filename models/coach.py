from datetime import datetime
from models import db


class CoachConversation(db.Model):
    __tablename__ = "coach_conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    relationship_id = db.Column(db.Integer, db.ForeignKey("relationships.id", ondelete="SET NULL"), nullable=True)
    user_message = db.Column(db.Text, nullable=False)
    ai_reply = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
