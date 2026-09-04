from datetime import datetime
from models import db

class RelationshipPlan(db.Model):
    __tablename__ = 'relationship_plans'

    id = db.Column(db.Integer, primary_key=True)
    relationship_id = db.Column(db.Integer, db.ForeignKey('relationships.id'), nullable=False)
    initial_score = db.Column(db.Float, default=0.0)
    target_score = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship('DailyTask', backref='plan', cascade="all, delete-orphan")

class DailyTask(db.Model):
    __tablename__ = 'daily_tasks'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('relationship_plans.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)