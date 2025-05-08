from datetime import timedelta
from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, DateTime
from app.extensions import db


class Subscription(db.Model):
    """Subscription Model for managing a user subscriptions"""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    auto_renew = Column(Boolean, default=True)
    start_date = Column(DateTime, server_default=db.func.now(), nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=db.func.now(), nullable=False)
    updated_at = Column(
        DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now()
    )

    __table_args__ = (
        Index("idx_subscription_user_plan", "user_id", "plan_id"),
        Index("idx_subscription_active", "is_active"),
        Index("idx_subscription_end_date", "end_date"),
        Index("idx_subscription_user_created", "user_id", "created_at"),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.end_date and self.plan:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_in_days)

    def __repr__(self):
        return f"<Subscription {self.user_id} - {self.plan_id}>"
