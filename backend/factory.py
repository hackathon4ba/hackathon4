from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from spectree import SecurityScheme, SpecTree
from flask_jwt_extended import JWTManager
from sqlalchemy import select
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = SpecTree(
    "flask",
    title="Flask Backend Template",
    version="v1.0",
    path="docs",
    security_schemes=[
        SecurityScheme(
            name="api_key",
            data={"type": "apiKey", "name": "Authorization", "in": "header"},
        )
    ],
    security={"api_key": []},
)


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(Config)

    from models import Restaurant, User

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.user_lookup_loader
    def user_load(header, data):
        account_type = data.get("account_type", "user")
        model = Restaurant if account_type == "restaurant" else User

        current_user = db.session.scalars(
            select(model).filter_by(email=data["sub"])
        ).first()

        return current_user

    from controllers import (
        auth_controller,
        dashboard_controller,
        menu_controller,
        order_controller,
        restaurant_controller,
        user_controller,
    )

    app.register_blueprint(user_controller)
    app.register_blueprint(auth_controller)
    app.register_blueprint(restaurant_controller)
    app.register_blueprint(menu_controller)
    app.register_blueprint(order_controller)
    app.register_blueprint(dashboard_controller)

    api.register(app)

    return app
