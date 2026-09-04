
from datetime import datetime

from models import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ---------------------------------------------------------
    # ONE-TO-ONE PERSONALITY PROFILE
    # ---------------------------------------------------------
    personality_profile = db.relationship(
        "PersonalityProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # ---------------------------------------------------------
    # ONE-TO-ONE ASTROLOGY PROFILE
    # ---------------------------------------------------------
    astrology_profile = db.relationship(
        "AstrologyProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # ---------------------------------------------------------
    # RELATIONSHIPS
    # ---------------------------------------------------------
    relationships = db.relationship(
        "Relationship",
        foreign_keys="Relationship.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ---------------------------------------------------------
    # CHAT ANALYSES
    # ---------------------------------------------------------
    chat_analyses = db.relationship(
        "ChatAnalysis",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ---------------------------------------------------------
    # PASSWORD METHODS
    # ---------------------------------------------------------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def __repr__(self):
        return f"<User {self.email}>"

