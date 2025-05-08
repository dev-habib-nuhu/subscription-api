from app import create_app
from app.extensions import db
from app.models.user_model import User
from app.models.plan_model import Plan


def seed_initial_data():
    app = create_app()
    with app.app_context():
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", email="admin@gmail.com")
            admin.set_password("admin123")
            db.session.add(admin)

        if not Plan.query.count():
            plans = [
                Plan(
                    name="Free",
                    description="Basic free plan",
                    price=0,
                    duration_in_days=30,
                ),
                Plan(
                    name="Basic",
                    description="Basic subscription",
                    price=4.99,
                    duration_in_days=30,
                ),
                Plan(
                    name="Pro",
                    description="Professional plan",
                    price=9.99,
                    duration_in_days=30,
                ),
                Plan(
                    name="Enterprise",
                    description="Enterprise solution",
                    price=19.99,
                    duration_in_days=30,
                ),
            ]
            db.session.add_all(plans)

        db.session.commit()
