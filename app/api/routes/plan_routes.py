from loguru import logger
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.plan_service import PlanService
from app.utils.response import error_response, success_response
from app.schemas import plan_list_schema, plan_schema
from marshmallow import ValidationError


plan_blueprint = Blueprint("plan", __name__)


@plan_blueprint.route("/", methods=["GET"])
def get_all_active_plans():
    """Get all active Plans"""
    try:
        plans = PlanService.get_all_active_plans()
        return success_response({"plans": plan_list_schema.dump(plans)})
    except Exception as ex:
        logger.exception(f"Failed to get all active plans on error: {ex}")
        return error_response("Internal server error", 500)


@plan_blueprint.route("/<int:plan_id>", methods=["GET"])
def get_plan(plan_id):
    """Get a plan by ID"""
    try:
        plan = PlanService.get_plan_by_id(plan_id)
        if not plan:
            return error_response("Plan not found", 404)
        return success_response({"plan": plan_schema.dump(plan)})
    except Exception as ex:
        logger.exception(f"Failed to get plan with ID {plan_id} on error: {ex}")
        return error_response("Internal server error", 500)


@plan_blueprint.route("/", methods=["POST"])
@jwt_required()
def create_plan():
    """Create a plan"""
    try:
        user_id = get_jwt_identity()

        data = request.get_json()
        if not data:
            return error_response("No input data provided", 400)

        try:
            validated_data = plan_schema.load(data)
        except ValidationError as err:
            return error_response(str(err.messages), 400)

        plan = PlanService.create_plan(
            name=validated_data["name"],
            description=validated_data.get("description"),
            price=validated_data["price"],
            duration_in_days=validated_data["duration_in_days"],
        )
        return success_response(plan_schema.dump(plan), 201)
    except ValidationError as err:
        return error_response(str(err.messages), 400)
    except Exception as ex:
        logger.exception(f"Failed to create plan on error {ex}")
        return error_response("Internal server error", 500)
