import pytest
from app.extensions import db
from app import create_app


class TestingConfig:
    """Test config class"""

    SECRET_KEY = "your_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True


@pytest.fixture
def app():
    """Create test Flask app with DB and create tables"""
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()

        yield app


@pytest.fixture
def client(app):
    """Test client with app context"""
    with app.test_client() as client:
        with app.app_context():
            yield client
