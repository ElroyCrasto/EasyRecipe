import os
from dotenv import load_dotenv

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
load_dotenv()


def start_app():
    # App Configuration
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Blueprints
    from .routes import page
    app.register_blueprint(page)

    # Database Configuration
    from .models import user, post, img
    db.init_app(app)

    # LoginManager
    loginManager = LoginManager()
    loginManager.login_view = "page.login"
    loginManager.init_app(app)

    @loginManager.user_loader
    def load_user(UID):
        return user.query.get(int(UID))

    return app
