from app.extensions import db
from app.models.plan_model import Plan


class PlanService:
    @staticmethod
    def create_plan(name: str, description: str, price: float, duration_in_days: int):
        """Add plan to the db"""
        plan = Plan(
            name=name,
            description=description,
            price=price,
            duration_in_days=duration_in_days,
        )
        db.session.add(plan)
        db.session.commit()
        return plan

    @staticmethod
    def get_all_active_plans():
        """Fetch all active plans from the database"""
        plans = Plan.query.filter_by(is_active=True).all()
        return plans

    @staticmethod
    def get_plan_by_id(plan_id: int):
        """Fetch a plan by its ID"""
        plan = Plan.query.get(plan_id)
        return plan
