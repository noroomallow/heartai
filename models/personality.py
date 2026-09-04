from datetime import datetime

from models import db


class PersonalityProfile(db.Model):
    __tablename__ = "personality_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    communication_style = db.Column(db.Float, nullable=True, default=0.0)
    emotional_openness = db.Column(db.Float, nullable=True, default=0.0)
    conflict_style = db.Column(db.Float, nullable=True, default=0.0)
    trust_level = db.Column(db.Float, nullable=True, default=0.0)
    social_preference = db.Column(db.Float, nullable=True, default=0.0)
    relationship_expectation = db.Column(db.Float, nullable=True, default=0.0)

    overall_score = db.Column(db.Float, nullable=True, default=0.0)
    relationship_score = db.Column(db.Float, nullable=True, default=0.0)
    personality_type = db.Column(db.String(100), nullable=True)

    interests_text = db.Column(db.Text, nullable=True)
    lifestyle_text = db.Column(db.Text, nullable=True)
    answers_json = db.Column(db.Text, nullable=True)

    compatibility_score = db.Column(db.Float, nullable=True, default=0.0)
    compatibility_data = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="personality_profile")

    def __repr__(self):
        return f"<PersonalityProfile user_id={self.user_id} score={self.overall_score}>"
