from datetime import datetime
import json

from models import db


class AstrologyProfile(db.Model):
    __tablename__ = "astrology_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    person_name = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.String(20), nullable=False)
    birth_time = db.Column(db.String(20), nullable=True)
    birth_place = db.Column(db.String(150), nullable=True)

    zodiac_sign = db.Column(db.String(50), nullable=True)
    moon_sign = db.Column(db.String(50), nullable=True)
    nakshatra = db.Column(db.String(100), nullable=True)

    personality_summary = db.Column(db.Text, nullable=True)
    career_summary = db.Column(db.Text, nullable=True)
    relationship_summary = db.Column(db.Text, nullable=True)
    strengths = db.Column(db.Text, nullable=True)
    challenges = db.Column(db.Text, nullable=True)
    ai_analysis = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="astrology_profile")
    readings = db.relationship(
        "AstrologyReading",
        back_populates="profile",
        cascade="all, delete-orphan",
        lazy=True,
    )


class AstrologyReading(db.Model):
    __tablename__ = "astrology_readings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey("astrology_profiles.id", ondelete="SET NULL"), nullable=True)

    mode = db.Column(db.String(20), nullable=False, default="single")
    person1_name = db.Column(db.String(200), nullable=False)
    person2_name = db.Column(db.String(200), nullable=True)

    person1_data = db.Column(db.Text, nullable=False)
    person2_data = db.Column(db.Text, nullable=True)
    combined_data = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    profile = db.relationship("AstrologyProfile", back_populates="readings")
    user = db.relationship("User", backref=db.backref("astrology_readings", cascade="all, delete-orphan"))

    @staticmethod
    def _load(value):
        if not value:
            return None
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return None

    def get_person1_data(self):
        return self._load(self.person1_data)

    def get_person2_data(self):
        return self._load(self.person2_data)

    def get_combined_data(self):
        return self._load(self.combined_data)
