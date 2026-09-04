import json
from models import db
from models.assessment import AssessmentSnapshot
from models.personality import PersonalityProfile
from models.compatibility import CompatibilityResult
from models.chat_analysis import ChatAnalysis
from models.relationship import Relationship
from models.relationship_plan import RelationshipPlan, DailyTask
from services.relationship_plan_service import PlanGeneratorService


class AssessmentService:
    WEIGHTS = {"personality": 0.30, "compatibility": 0.40, "chat": 0.30}

    @staticmethod
    def category(score):
        if score >= 90:
            return "Excellent Relationship Health"
        if score >= 80:
            return "Strong Relationship Health"
        if score >= 65:
            return "Good Relationship Health"
        if score >= 50:
            return "Developing Relationship Health"
        if score >= 35:
            return "Needs Improvement"
        return "Needs Focus"

    @staticmethod
    def calculate(user_id, relationship_id=None, save=True):
        personality = PersonalityProfile.query.filter_by(user_id=user_id).first()
        rel = Relationship.query.filter_by(user_id=user_id, status="active").order_by(Relationship.id.desc()).first()
        relationship_id = relationship_id or (rel.id if rel else None)

        compatibility = None
        if relationship_id:
            compatibility = CompatibilityResult.query.filter_by(relationship_id=relationship_id).order_by(CompatibilityResult.id.desc()).first()
        chat = ChatAnalysis.query.filter_by(user_id=user_id).order_by(ChatAnalysis.id.desc()).first()

        scores = {}
        if personality and personality.overall_score is not None and personality.answers_json:
            scores["personality"] = max(0.0, min(100.0, float(personality.overall_score)))
        if compatibility:
            scores["compatibility"] = max(0.0, min(100.0, float(compatibility.overall_score or 0)))
        if chat:
            chat_components = [float(chat.communication_score or 0), float(chat.emotional_score or 0), float(chat.trust_score or 0), float(chat.compatibility_score or 0)]
            scores["chat"] = max(0.0, min(100.0, sum(chat_components) / len(chat_components)))

        if not scores:
            return None

        weight_total = sum(AssessmentService.WEIGHTS[k] for k in scores)
        overall = round(sum(scores[k] * AssessmentService.WEIGHTS[k] for k in scores) / weight_total, 1)
        breakdown = {
            "personality": round(scores.get("personality", 0), 1),
            "compatibility": round(scores.get("compatibility", 0), 1),
            "chat": round(scores.get("chat", 0), 1),
            "weights_used": {k: AssessmentService.WEIGHTS[k] for k in scores},
            "tests_completed": len(scores),
        }

        result = {
            "overall_score": overall,
            "category": AssessmentService.category(overall),
            "personality_score": breakdown["personality"],
            "compatibility_score": breakdown["compatibility"],
            "chat_score": breakdown["chat"],
            "emotional_score": float(chat.emotional_score or 0) if chat else 0,
            "trust_score": float(chat.trust_score or 0) if chat else 0,
            "tests_completed": len(scores),
            "breakdown": breakdown,
            "personality": personality,
            "compatibility": compatibility,
            "chat": chat,
            "relationship": rel,
        }

        if save and relationship_id:
            snapshot = AssessmentSnapshot(
                user_id=user_id,
                relationship_id=relationship_id,
                overall_score=overall,
                category=result["category"],
                personality_score=result["personality_score"],
                compatibility_score=result["compatibility_score"],
                chat_score=result["chat_score"],
                emotional_score=result["emotional_score"],
                trust_score=result["trust_score"],
                tests_completed=len(scores),
                score_breakdown=json.dumps(breakdown),
            )
            db.session.add(snapshot)
            db.session.commit()

        return result

    @staticmethod
    def plan_profile(score):
        if score < 35:
            return "Intensive Foundation", "Focus strongly on communication, trust, conflict handling and emotional safety."
        if score < 50:
            return "Foundation Building", "Build basic communication, trust, listening and shared understanding."
        if score < 65:
            return "Growth Plan", "Improve consistency, emotional openness, conflict resolution and connection."
        if score < 80:
            return "Strengthening Plan", "Strengthen good habits and address remaining weak areas."
        if score < 90:
            return "Advanced Connection", "Maintain strengths while deepening communication and emotional connection."
        return "Maintenance & Growth", "Maintain strong relationship habits and continue meaningful connection."

    @staticmethod
    def ensure_plan(assessment):
        """Return the active 30-day plan, creating it safely for SQLite.

        The old implementation deleted/committed an incomplete plan and then
        immediately inserted a new one. Two browser requests could therefore
        contend for SQLite's single writer lock. This version keeps one
        transaction, avoids an unnecessary delete/commit cycle, and retries a
        short SQLite lock after rolling the transaction back.
        """
        import time
        from sqlalchemy.exc import OperationalError

        rel = assessment.get("relationship") if assessment else None
        if not rel:
            return None

        existing = (
            RelationshipPlan.query
            .filter_by(relationship_id=rel.id, status="active")
            .order_by(RelationshipPlan.id.desc())
            .first()
        )
        if existing and DailyTask.query.filter_by(plan_id=existing.id).count() >= 30:
            return existing

        score = float(assessment["overall_score"])
        scores = {
            "personality": assessment.get("personality_score", 0),
            "compatibility": assessment.get("compatibility_score", 0),
            "chat": assessment.get("chat_score", 0),
            "overall_score": score,
        }
        partner_name = getattr(rel, "partner_name", "your partner") or "your partner"
        tasks = PlanGeneratorService.build_30_day_plan(scores, partner_name)

        for attempt in range(3):
            try:
                # Re-check inside each attempt because another request may
                # have created the plan while this transaction was waiting.
                plan = (
                    RelationshipPlan.query
                    .filter_by(relationship_id=rel.id, status="active")
                    .order_by(RelationshipPlan.id.desc())
                    .first()
                )

                if plan and DailyTask.query.filter_by(plan_id=plan.id).count() >= 30:
                    return plan

                if plan:
                    # Complete an existing incomplete plan rather than deleting
                    # it, which substantially reduces SQLite write contention.
                    for task in list(plan.tasks or []):
                        db.session.delete(task)
                else:
                    plan = RelationshipPlan(
                        relationship_id=rel.id,
                        initial_score=score,
                        target_score=min(100.0, round(score + (10 if score < 80 else 5), 1)),
                        status="active",
                    )
                    db.session.add(plan)
                    db.session.flush()

                for item in tasks[:30]:
                    db.session.add(DailyTask(
                        plan_id=plan.id,
                        day_number=int(item.get("day", 1)),
                        week_number=int(item.get("week", 1)) if str(item.get("week", 1)).isdigit() else 1,
                        title=str(item.get("title", "Relationship Activity")),
                        description=str(item.get("description", "Spend meaningful time together.")),
                    ))

                db.session.commit()
                return plan

            except OperationalError as exc:
                db.session.rollback()
                if "database is locked" not in str(exc).lower() or attempt >= 2:
                    raise
                time.sleep(1.0 * (attempt + 1))

        return None

