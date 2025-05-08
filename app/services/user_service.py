from sqlalchemy import or_
from app.extensions import db

from app.models.user_model import User


class UserService:
    """Service handles user related database operations"""

    @staticmethod
    def create_user(username: str, email: str, password: str):
        """Add user to the db"""
        user = User(username=username, email=email, pass_hash=password)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_details_by_id(user_id: str):
        """Fetches users details from database given user id"""
        user = User.query.filter_by(id=user_id, is_active=True).first()
        return user

    @staticmethod
    def get_user_details_by_username(username: str):
        """Fetches users details from database given username"""
        user = User.query.filter_by(username=username, is_active=True).first()
        return user

    @staticmethod
    def user_exists(username: str, email: str):
        """
        Check if a user exists with the given username or email.
        """
        user = User.query.filter(
            or_(User.username == username, User.email == email)
        ).first()
        return user

    @staticmethod
    def authenticate_user(username: str, password: str):
        """Authenticate user with username and password"""
        users_data = UserService.get_user_details_by_username(username)
        if not users_data:
            return None
        user = User.query.get(users_data.id)
        if user and user.check_password(password):
            return user
        return None
