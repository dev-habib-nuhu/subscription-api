from loguru import logger
from app.schemas import subscription_list_schema, subscription_schema
from app.utils.response import success_response, error_response
from flask import Blueprint, request
from app.services.subscription_service import SubscriptionService
from flask_jwt_extended import jwt_required, get_jwt_identity

subscription_blueprint = Blueprint("subscription", __name__)


@subscription_blueprint.route("/", methods=["POST"])
@jwt_required()
def create_subscription():
    """Create a subscription"""
    data = request.get_json()
    plan_id = data.get("plan_id")
    auto_renew = data.get("auto_renew", True)
    user_id = get_jwt_identity()

    if not plan_id:
        return error_response("Plan ID is required", 400)

    try:
        result = SubscriptionService.create_subscription(user_id, plan_id, auto_renew)
        subscription = subscription_schema.dump(result)
        return success_response(
            {"subscription": subscription},
            201,
        )
    except Exception as ex:
        logger.error(f"Error creating subscription: {ex}")
        return error_response("Failed to create subscription", 500)


@subscription_blueprint.route("/active", methods=["GET"])
@jwt_required()
def get_active_subscriptions():
    """Get active subscriptions"""
    user_id = get_jwt_identity()
    cursor = request.args.get("cursor")
    limit = min(int(request.args.get("limit", 10)), 100)
    try:
        result = SubscriptionService.get_active_subscriptions(user_id, cursor, limit)
        subscriptions = subscription_list_schema.dump(result["data"], many=True)
        return success_response(
            {
                "subscriptions": subscriptions,
                "pagination": result["pagination"],
            },
            200,
        )
    except Exception as ex:
        logger.error(f"Error fetching active subscriptions: {ex}")
        return error_response("Failed to fetch active subscriptions", 500)


@subscription_blueprint.route("/history", methods=["GET"])
@jwt_required()
def get_subscription_history():
    """Get subscription history"""
    user_id = get_jwt_identity()
    cursor = request.args.get("cursor")
    limit = min(int(request.args.get("limit", 10)), 100)
    try:
        result = SubscriptionService.get_subscription_history(user_id, cursor, limit)
        subscriptions = subscription_list_schema.dump(result["data"], many=True)
        return success_response(
            {
                "subscriptions": subscriptions,
                "pagination": result["pagination"],
            },
            200,
        )
    except Exception as ex:
        logger.error(f"Error fetching subscription history: {ex}")
        return error_response("Failed to fetch subscription history", 500)


@subscription_blueprint.route("/<int:subscription_id>/upgrade", methods=["GET"])
@jwt_required()
def upgrade_subscription(subscription_id):
    """Upgrade a subscription"""
    data = request.get_json()
    new_plan_id = data.get("new_plan_id")
    user_id = get_jwt_identity()
    if not new_plan_id:
        return error_response("New plan ID is required", 400)

    try:
        subscription = SubscriptionService.upgrade_subscription(
            subscription_id, new_plan_id
        )
        if not subscription:
            return error_response("Subscription not found", 404)
        return success_response(
            {
                "subscription_id": subscription.id,
                "plan_id": subscription.plan_id,
                "end_date": subscription.end_date,
            },
            200,
        )
    except Exception as ex:
        logger.error(f"Error upgrading subscription: {ex}")
        return error_response("Failed to upgrade subscription", 500)


@subscription_blueprint.route("<int:subscription_id>/cancel", methods=["PUT"])
@jwt_required()
def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    user_id = get_jwt_identity()
    try:
        subscription = SubscriptionService.cancel_subscription(subscription_id)
        if not subscription:
            return error_response("Subscription not found", 404)
        return success_response(
            {
                "message": "Subscription cancelled successfully",
            },
            200,
        )
    except Exception as ex:
        logger.error(f"Error cancelling subscription: {ex}")
        return error_response("Failed to cancel subscription", 500)
