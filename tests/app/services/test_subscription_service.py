import pytest
from unittest.mock import ANY, patch, MagicMock
from app.services.subscription_service import SubscriptionService
from app.models.subscription_model import Subscription
from app.models.plan_model import Plan
from flask import Flask
from app.extensions import db


@pytest.fixture
def app():
    """Create test Flask app with DB"""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


@pytest.fixture
def client(app):
    """Test client with app context"""
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_create_subscription(app, client):
    """Test subscription creation with proper app context"""
    with app.app_context():
        mock_plan = MagicMock(spec=Plan)
        mock_plan.is_active = True
        mock_plan.duration_in_days = 30

        mock_sub = MagicMock(spec=Subscription)
        mock_sub.user_id = "user1"
        mock_sub.plan_id = 1
        mock_sub.is_active = True
        mock_sub.auto_renew = True

        with patch(
            "app.services.subscription_service.Plan.query"
        ) as mock_plan_query, patch(
            "app.services.subscription_service.Subscription"
        ) as mock_sub_cls, patch(
            "app.services.subscription_service.db.session"
        ) as mock_session:
            mock_plan_query.get.return_value = mock_plan
            mock_sub_cls.return_value = mock_sub

            result = SubscriptionService.create_subscription(
                user_id="user1", plan_id=1, auto_renew=True
            )

            mock_plan_query.get.assert_called_once_with(1)
            mock_sub_cls.assert_called_once_with(
                user_id="user1",
                plan_id=1,
                start_date=ANY,
                end_date=ANY,
                auto_renew=True,
                is_active=True,
            )
            mock_session.add.assert_called_once_with(mock_sub)
            mock_session.commit.assert_called_once()
            assert result == mock_sub


def test_upgrade_subscription(app):
    """Test subscription upgrade with app context"""
    with app.app_context():
        mock_result = MagicMock()
        mock_row = {"id": 1, "plan_id": 2}
        mock_result.fetchone.return_value = mock_row

        with patch("app.services.subscription_service.text"), patch(
            "app.services.subscription_service.db.session.execute"
        ) as mock_execute:
            mock_execute.return_value = mock_result

            result = SubscriptionService.upgrade_subscription(1, 2)

            mock_execute.assert_called_once()
            assert result == mock_row


def test_cancel_subscription(app):
    """Test subscription cancellation"""
    with app.app_context():
        mock_sub = MagicMock(spec=Subscription)
        mock_sub.is_active = True
        mock_sub.auto_renew = True

        with patch(
            "app.services.subscription_service.Subscription.query"
        ) as mock_query, patch("app.services.subscription_service.db.session.commit"):
            mock_query.get.return_value = mock_sub

            result = SubscriptionService.cancel_subscription(1)

            mock_query.get.assert_called_once_with(1)
            assert mock_sub.is_active is False
            assert mock_sub.auto_renew is False
            assert result == mock_sub


def test_get_subscription_history(app):
    with app.app_context():
        mock_result = {
            "data": ["subscription1", "subscription2"],
            "pagination": {"next_cursor": "2025-06-01T10:00:00", "has_more": True},
        }

        with patch.object(
            SubscriptionService, "_fetch_subscriptions", return_value=mock_result
        ) as mock_fetch:
            result = SubscriptionService.get_subscription_history(
                user_id="user1", cursor="2025-06-01T09:00:00", limit=5
            )

            mock_fetch.assert_called_once_with(
                user_id="user1",
                cursor="2025-06-01T09:00:00",
                limit=5,
                cursor_field="created_at",
                order_by="DESC",
            )
            assert result == mock_result


def test_get_active_subscriptions(app):
    with app.app_context():
        mock_result = {
            "data": ["subscriptionA", "subscriptionB"],
            "pagination": {"next_cursor": "2025-06-10T14:00:00", "has_more": False},
        }

        with patch.object(
            SubscriptionService, "_fetch_subscriptions", return_value=mock_result
        ) as mock_fetch:
            result = SubscriptionService.get_active_subscriptions(
                user_id="user123", cursor="2025-06-10T13:00:00", limit=3
            )

            mock_fetch.assert_called_once_with(
                user_id="user123",
                cursor="2025-06-10T13:00:00",
                limit=3,
                cursor_field="end_date",
                active_only=True,
                future_only=True,
            )
            assert result == mock_result


