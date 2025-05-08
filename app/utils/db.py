from app.extensions import db


def init_db(app):
    """Initialize the database with the app context."""
    with app.app_context():
        db.create_all()
