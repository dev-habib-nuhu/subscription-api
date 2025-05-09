from flask import request, Blueprint
from app.schemas import user_schema
from app.services.user_service import UserService
from app.utils.response import error_response, success_response
from flask_jwt_extended import create_access_token


user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/signup", methods=["POST"])
def create_account():
    """Create a new user account"""
    data = request.get_json()
    if not data:
        return error_response("Invalid request", 400)
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not all([username, email, password]):
        return error_response(
            "Username, password and email is required to create an account", 400
        )

    # check if user already already has account
    existing_user = UserService.user_exists(username, email)
    if existing_user:
        if existing_user.username == username:
            return error_response("Username already exists", 409)
        if existing_user.email == email:
            return error_response("Email already exists", 409)

    # create a new user
    user = UserService.create_user(username, email, password)
    if not user:
        return error_response("Failed to create user", 500)

    return success_response({"user": user_schema.dump(user)}, 201)


@user_blueprint.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get user details by ID"""
    user = UserService.get_user_details_by_id(user_id)
    if not user:
        return error_response("User not found", 404)
    return success_response(user_schema.dump(user), 200)


@user_blueprint.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return error_response("Invalid request", 400)
    username = data.get("username")
    password = data.get("password")
    if not all([username, password]):
        return error_response("Username and password is required to login", 400)

    # authenticate the user if details are valid
    user = UserService.authenticate_user(username, password)
    if not user:
        return error_response("Invalid username or password", 401)

    access_token = create_access_token(identity=str(user.id))
    return success_response({"access_token": access_token, "user_id": user.id}, 200)
