import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from flask_jwt_extended import create_access_token
from app.models.subscription_model import Subscription
from app.models.plan_model import Plan


@pytest.fixture
def auth_headers():
    token = create_access_token(identity="1")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture
def sample_plan():
    return Plan(
        id=1,
        name="Premium Plan",
        description="Premium features",
        price=19.99,
        duration_in_days=30,
        is_active=True,
    )


@pytest.fixture
def sample_subscription(sample_plan):
    return Subscription(
        id=1,
        user_id=1,
        plan_id=sample_plan.id,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
        is_active=True,
        auto_renew=True,
    )


def test_create_subscription_success(client, auth_headers, sample_plan):
    with patch(
        "app.services.subscription_service.SubscriptionService.create_subscription"
    ) as mock_create:
        mock_create.return_value = Subscription(
            id=1,
            user_id=1,
            plan_id=sample_plan.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=30),
            is_active=True,
            auto_renew=True,
        )

        response = client.post(
            "/api/v1/subscriptions/",
            json={"plan_id": sample_plan.id, "auto_renew": True},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == "success"
        assert "subscription" in data["data"]
        subscription = data["data"]["subscription"]
        assert subscription["plan_id"] == sample_plan.id
        assert subscription["is_active"] is True
        assert subscription["auto_renew"] is True


def test_create_subscription_missing_plan_id(client, auth_headers):
    """Test subscription creation fails when missing plan_id"""
    response = client.post(
        "/api/v1/subscriptions/", json={"auto_renew": True}, headers=auth_headers
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert "Plan ID is required" in data["message"]


def test_get_active_subscriptions(
    client, auth_headers, sample_subscription, sample_plan
):
    """Test getting active subscriptions"""
    mock_result = {
        "data": [
            {
                "id": sample_subscription.id,
                "user_id": sample_subscription.user_id,
                "plan_id": sample_subscription.plan_id,
                "start_date": sample_subscription.start_date,
                "end_date": sample_subscription.end_date,
                "is_active": sample_subscription.is_active,
                "auto_renew": sample_subscription.auto_renew,
                "created_at": datetime.now(timezone.utc),
                "plan": {
                    "id": sample_plan.id,
                    "name": sample_plan.name,
                    "price": float(sample_plan.price),
                    "description": sample_plan.description,
                    "duration_in_days": sample_plan.duration_in_days,
                },
            }
        ],
        "pagination": {"next_cursor": None, "has_more": False},
    }

    with patch(
        "app.services.subscription_service.SubscriptionService.get_active_subscriptions"
    ) as mock_get:
        mock_get.return_value = mock_result

        response = client.get("/api/v1/subscriptions/active", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "subscriptions" in data["data"]
        assert "pagination" in data["data"]
        subscriptions = data["data"]["subscriptions"]
        assert len(subscriptions) == 1
        assert subscriptions[0]["id"] == sample_subscription.id
        assert subscriptions[0]["is_active"] is True


def test_get_active_subscriptions_with_pagination(client, auth_headers):
    """Test getting active subscriptions with pagination"""
    cursor = "2025-01-01T00:00:00"
    limit = 5

    with patch(
        "app.services.subscription_service.SubscriptionService.get_active_subscriptions"
    ) as mock_get:
        mock_get.return_value = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        response = client.get(
            f"/api/v1/subscriptions/active?cursor={cursor}&limit={limit}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        mock_get.assert_called_once_with("1", cursor, limit)


def test_get_subscription_history(
    client, auth_headers, sample_subscription, sample_plan
):
    """Test GET subscription history"""
    mock_result = {
        "data": [
            {
                "id": sample_subscription.id,
                "user_id": sample_subscription.user_id,
                "plan_id": sample_subscription.plan_id,
                "start_date": sample_subscription.start_date,
                "end_date": sample_subscription.end_date,
                "is_active": sample_subscription.is_active,
                "auto_renew": sample_subscription.auto_renew,
                "created_at": datetime.now(timezone.utc),
                "plan": {
                    "id": sample_plan.id,
                    "name": sample_plan.name,
                    "price": float(sample_plan.price),
                    "description": sample_plan.description,
                    "duration_in_days": sample_plan.duration_in_days,
                },
            }
        ],
        "pagination": {"next_cursor": None, "has_more": False},
    }

    with patch(
        "app.services.subscription_service.SubscriptionService.get_subscription_history"
    ) as mock_get:
        mock_get.return_value = mock_result

        response = client.get("/api/v1/subscriptions/history", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "subscriptions" in data["data"]
        assert "pagination" in data["data"]
        subscriptions = data["data"]["subscriptions"]
        assert len(subscriptions) == 1
        assert subscriptions[0]["id"] == sample_subscription.id


def test_get_subscription_history_with_pagination(client, auth_headers):
    """Test GET subscription history with pagination"""
    cursor = "2025-01-01T00:00:00"
    limit = 5

    with patch(
        "app.services.subscription_service.SubscriptionService.get_subscription_history"
    ) as mock_get:
        mock_get.return_value = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        response = client.get(
            f"/api/v1/subscriptions/history?cursor={cursor}&limit={limit}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        mock_get.assert_called_once_with("1", cursor, limit)


def test_upgrade_subscription_success(client, auth_headers, sample_subscription):
    """Test subscription upgrade"""
    new_plan_id = 2
    mock_subscription = Subscription(
        id=sample_subscription.id,
        user_id=1,
        plan_id=new_plan_id,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=60),
        is_active=True,
        auto_renew=True,
    )

    with patch(
        "app.services.subscription_service.SubscriptionService.upgrade_subscription"
    ) as mock_upgrade:
        mock_upgrade.return_value = mock_subscription

        response = client.get(
            f"/api/v1/subscriptions/{sample_subscription.id}/upgrade",
            json={"new_plan_id": new_plan_id},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["data"]["subscription_id"] == sample_subscription.id
        assert data["data"]["plan_id"] == new_plan_id


def test_cancel_subscription_success(client, auth_headers, sample_subscription):
    """Test subscription cancellation"""
    mock_subscription = Subscription(
        id=sample_subscription.id,
        user_id=1,
        plan_id=1,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
        is_active=False,
        auto_renew=False,
    )

    with patch(
        "app.services.subscription_service.SubscriptionService.cancel_subscription"
    ) as mock_cancel:
        mock_cancel.return_value = mock_subscription

        response = client.put(
            f"/api/v1/subscriptions/{sample_subscription.id}/cancel",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "Subscription cancelled successfully" in data["data"]["message"]
