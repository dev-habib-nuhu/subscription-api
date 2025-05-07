from sqlalchemy import Boolean, Column, Integer, String, DateTime
from app.extensions import db


class SubscriptionPlan(db.Model):
    """Subscription Plan model holds the details of subscription plans"""

    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), nullable=False)
    price = Column(Integer, nullable=False)
    duration_in_days = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=db.func.now(), nullable=False)
    updated_at = Column(
        DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now()
    )

    subscriptions = db.relationship(
        "Subscription", backref="subscription_plan", lazy="dynamic"
    )

    def __repr__(self):
        return f"<SubscriptionPlan {self.name}>"
