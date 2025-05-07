from flask import Flask
from .extensions import db, migrate, jwt
from .config import Config
from app.api.routes.user_routes import user_blueprint

API_VERSION = "v1"

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(user_blueprint, url_prefix="/api/{API_VERSION}/user")
    return app
