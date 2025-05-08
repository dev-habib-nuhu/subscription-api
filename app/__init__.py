from flask import Flask
from .extensions import db, migrate, jwt
from .config import Config
from app.api.routes.user_routes import user_blueprint
from app.api.routes.subscription_routes import subscription_blueprint
from app.api.routes.plan_routes import plan_blueprint

API_VERSION = "v1"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(user_blueprint, url_prefix=f"/api/{API_VERSION}/user")
    app.register_blueprint(
        subscription_blueprint, url_prefix=f"/api/{API_VERSION}/subscription"
    )
    app.register_blueprint(plan_blueprint, url_prefix=f"/api/{API_VERSION}/plan")
    return app
