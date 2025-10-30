from flask import Flask, send_from_directory
from flask_migrate import Migrate
from flask_cors import CORS
from app.extensions import db
from config import Config
from flask_jwt_extended import JWTManager
import os

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folder exists
    if not hasattr(app.config, "UPLOAD_FOLDER") or not app.config.get("UPLOAD_FOLDER"):
        app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ✅ Proper CORS setup (works for dev + production)
    CORS(
        app,
        origins=[
            "http://localhost:5173",                          # local dev frontend
            "https://www.btx-capital.com/",      # production frontend
        ],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)

    # Import models so Alembic can detect them
    from app import models  # ✅ important for migrations

    # Register blueprints
    from app.routes.contacts import contacts_bp
    from app.routes.auth import auth_bp
    from app.routes.news import news_bp

    app.register_blueprint(contacts_bp, url_prefix="/api/contacts")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(news_bp, url_prefix="/api/news")

    # Serve uploaded files
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app
