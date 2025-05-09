from sqlalchemy import Boolean, Column, Index, Integer, String, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """User Model to save user details"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    pass_hash = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=db.func.now(), nullable=False)
    updated_at = Column(
        DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now()
    )
    subscriptions = db.relationship("Subscription", backref="user", lazy="dynamic")

    def set_password(self, passwrd):
        self.pass_hash = generate_password_hash(passwrd)

    def check_password(self, passwrd):
        return check_password_hash(self.pass_hash, passwrd)

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_username", "username"),
    )

    def __repr__(self):
        return f"<User {self.username}>"
