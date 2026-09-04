from datetime import datetime

from models import db


class Relationship(db.Model):
    __tablename__ = "relationships"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    partner_name = db.Column(db.String(100), nullable=False)
    partner_email = db.Column(db.String(120), nullable=True)
    relationship_type = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(30), default="active", nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", foreign_keys=[user_id], back_populates="relationships")
    partner = db.relationship("User", foreign_keys=[user2_id])

    compatibility_results = db.relationship(
        "CompatibilityResult",
        back_populates="relationship",
        cascade="all, delete-orphan",
    )
    chat_analyses = db.relationship(
        "ChatAnalysis",
        back_populates="relationship",
        cascade="all, delete-orphan",
    )

    @property
    def user1_id(self):
        return self.user_id

    @user1_id.setter
    def user1_id(self, value):
        self.user_id = value

    def __repr__(self):
        return f"<Relationship id={self.id} user_id={self.user_id} partner_name='{self.partner_name}'>"
