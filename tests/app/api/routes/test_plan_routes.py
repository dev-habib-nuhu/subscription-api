from flask_jwt_extended import create_access_token
import pytest
from unittest.mock import patch
from app.models.plan_model import Plan
import pytest


@pytest.fixture
def auth_headers():
    """Fixture to return authentication headers"""
    token = create_access_token("test@example.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_plan():
    return Plan(
        id=1,
        name="Premium Plan",
        description="Premium features",
        price=999,
        duration_in_days=30,
        is_active=True,
    )


def test_get_all_active_plans(client):
    """Test getting all active plans"""
    with patch(
        "app.services.plan_service.PlanService.get_all_active_plans"
    ) as mock_get_plans:
        plan = Plan(
            id=1,
            name="Premium Plan",
            description="Premium features",
            price=999,
            duration_in_days=30,
            is_active=True,
        )
        mock_get_plans.return_value = [plan]

        response = client.get("/api/v1/plans/")
        assert response.status_code == 200
        data = response.get_json()
        assert "plans" in data["data"]
        assert len(data["data"]["plans"]) == 1
        plan_data = data["data"]["plans"][0]
        assert plan_data["name"] == "Premium Plan"
        assert plan_data["price"] == 999
        assert plan_data["duration_in_days"] == 30
        mock_get_plans.assert_called_once()


def test_get_plan_by_id(client, sample_plan):
    """Test getting a specific plan by ID"""
    with patch("app.services.plan_service.PlanService.get_plan_by_id") as mock_get_plan:
        mock_get_plan.return_value = sample_plan
        response = client.get("/api/v1/plans/1")
        assert response.status_code == 200
        data = response.get_json()
        assert "plan" in data["data"]
        plan_data = data["data"]["plan"]
        assert plan_data["id"] == 1
        assert plan_data["name"] == "Premium Plan"
        assert plan_data["price"] == 999
        assert plan_data["duration_in_days"] == 30
        mock_get_plan.assert_called_once_with(1)


def test_get_plan_not_found(client):
    """Test getting a non-existent plan"""
    with patch("app.services.plan_service.PlanService.get_plan_by_id") as mock_get_plan:
        mock_get_plan.return_value = None
        response = client.get("/api/v1/plans/999")
        assert response.status_code == 404
        data = response.get_json()
        assert data["message"] == "Plan not found"


def test_create_plan(client, auth_headers):
    """Test creating a new plan"""
    plan_data = {
        "name": "New Plan",
        "description": "New plan description",
        "price": 19.22,
        "duration_in_days": 30,
    }

    with patch("app.services.plan_service.PlanService.create_plan") as mock_create_plan:
        plan = Plan(
            name=plan_data["name"],
            description=plan_data["description"],
            price=plan_data["price"],
            duration_in_days=plan_data["duration_in_days"],
            is_active=True,
        )
        mock_create_plan.return_value = plan

        response = client.post("/api/v1/plans/", json=plan_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == "success"
        plan_data = data["data"]
        assert plan_data["name"] == "New Plan"
        assert plan_data["price"] == 19.22
        assert plan_data["duration_in_days"] == 30
        mock_create_plan.assert_called_once_with(
            name=plan_data["name"],
            description=plan_data["description"],
            price=plan_data["price"],
            duration_in_days=plan_data["duration_in_days"],
        )


def test_create_plan_unauthorized(client):
    """Test creating a plan without authentication"""
    plan_data = {
        "name": "New Plan",
        "description": "New plan description",
        "price": 19.22,
        "duration_in_days": 30,
    }
    response = client.post("/api/v1/plans/", json=plan_data)

    assert response.status_code == 401
    data = response.get_json()
    assert data["msg"] == "Missing Authorization Header"
