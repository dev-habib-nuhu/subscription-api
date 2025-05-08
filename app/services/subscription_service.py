from datetime import datetime, timedelta
from app.extensions import db
from app.models.subscription_model import Subscription
from app.models.plan_model import Plan
from sqlalchemy import text
from dateutil.parser import parse as parse_datetime


class SubscriptionService:
    """Service handles subscrition database operations"""

    @staticmethod
    def get_active_subscriptions(user_id: str, cursor=None, limit=10):
        return SubscriptionService._fetch_subscriptions(
            user_id=user_id,
            cursor=cursor,
            limit=limit,
            cursor_field="end_date",
            active_only=True,
            future_only=True,
        )

    @staticmethod
    def create_subscription(user_id: str, plan_id: int, auto_renew: bool = True):
        """Add subscription to the db"""
        plan = Plan.query.get(plan_id)
        if not plan or not plan.is_active:
            raise ValueError("Invalid or inactive subscription plan")
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=plan.duration_in_days)

        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            auto_renew=auto_renew,
            is_active=True,
        )
        db.session.add(subscription)
        db.session.commit()
        return subscription

    @staticmethod
    def upgrade_subscription(subscription_id: int, new_plan_id: int):
        """Upgrade a user subscription to a new plan"""
        sql_query = text(
            """
            WITH plan_info AS (
                SELECT duration_in_days FROM plans WHERE id = :new_plan_id
            )
            UPDATE subscriptions
            SET plan_id = :new_plan_id,
                end_date = DATE(end_date, '+' || (SELECT duration_in_days FROM plan_info) || ' days')
            WHERE id = :subscription_id
            RETURNING *
        """
        )
        result = db.session.execute(
            sql_query,
            {
                "subscription_id": subscription_id,
                "new_plan_id": new_plan_id,
            },
        )
        db.session.commit()
        return result.fetchone()

    @staticmethod
    def get_subscription_history(user_id: str, cursor=None, limit=10):
        return SubscriptionService._fetch_subscriptions(
            user_id=user_id,
            cursor=cursor,
            limit=limit,
            cursor_field="created_at",
            order_by="DESC",
        )

    @staticmethod
    def cancel_subscription(subscription_id: int):
        """Cancle a users subscription"""
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")
        subscription.is_active = False
        subscription.auto_renew = False
        db.session.commit()
        return subscription

    @staticmethod
    def _fetch_subscriptions(
        user_id: str,
        cursor=None,
        limit=10,
        cursor_field="created_at",
        active_only=False,
        future_only=False,
        order_by="DESC",
    ):
        """Internal method to fetch subscriptions based on filters"""
        limit = min(max(1, limit), 100)
        cursor_date = None
        if cursor:
            try:
                cursor_date = datetime.fromisoformat(cursor)
            except ValueError:
                raise ValueError("Invalid cursor format.")

        filters = ["s.user_id = :user_id"]
        if active_only:
            filters.append("s.is_active = TRUE")
        if future_only:
            filters.append("s.end_date > CURRENT_TIMESTAMP")
        if cursor_date:
            filters.append(f"s.{cursor_field} < :cursor_date")

        filter_clause = " AND ".join(filters)
        sql_query = text(
            f"""
            SELECT 
                s.id,
                s.user_id,
                s.plan_id,
                s.start_date,
                s.end_date,
                s.is_active,
                s.auto_renew,
                s.created_at,
                p.name as plan_name,
                p.price as plan_price,
                p.description as plan_description,
                p.duration_in_days as plan_duration_in_days,
                strftime('%Y-%m-%dT%H:%M:%S', s.{cursor_field}) as cursor_value
            FROM subscriptions s
            JOIN plans p ON s.plan_id = p.id
            WHERE {filter_clause}
            ORDER BY s.{cursor_field} {order_by}
            LIMIT :limit
        """
        )

        params = {"user_id": user_id, "limit": limit}
        if cursor_date:
            params["cursor_date"] = cursor_date

        result = db.session.execute(sql_query, params)
        rows = result.fetchall()

        data = []
        next_cursor = None
        if rows:
            for row in rows:
                subscription = {
                    "id": row.id,
                    "user_id": row.user_id,
                    "plan_id": row.plan_id,
                    "start_date": parse_datetime(row.start_date),
                    "end_date": parse_datetime(row.end_date),
                    "is_active": bool(row.is_active),
                    "auto_renew": bool(row.auto_renew),
                    "created_at": parse_datetime(row.created_at),
                    "plan": {
                        "id": row.plan_id,
                        "name": row.plan_name,
                        "price": float(row.plan_price),
                        "description": row.plan_description,
                        "duration_in_days": row.plan_duration_in_days,
                    },
                }
                data.append(subscription)
            last_item = rows[-1]
            next_cursor = last_item.cursor_value

        return {
            "data": data,
            "pagination": {
                "next_cursor": next_cursor,
                "has_more": len(data) == limit,
            },
        }
