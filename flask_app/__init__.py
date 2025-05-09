from flask import Flask
from flask_migrate import Migrate  # Ensure Migrate is imported
import os
from dotenv import load_dotenv
import click
import requests

# from commands.add_books import register_commands

# Load environment variables from .env file
load_dotenv()


def register_extensions(app):
    """Registers Flask extensions

    Args:
      app (app): The Flask application
    """
    from .modules.extensions import db
    from flask_cors import CORS

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "postgres")  # Keep default
    db_port = os.getenv("DB_PORT", "5432")  # Keep default
    db_name = os.getenv("DB_NAME")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize db first
    db.init_app(app)
    # Then initialize Migrate
    Migrate(app, db)
    
    # Enable CORS for all routes
    CORS(app)


def create_app():

    app = Flask(__name__)
    with app.app_context():

        # Load configuration from environment variables
        app.config.from_mapping(
            SECRET_KEY=os.getenv("SECRET_KEY"),
            DEBUG=os.getenv("DEBUG", True),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        register_extensions(app)

        # Register blueprints
        from flask_app.routes.views import views
        from flask_app.routes.api import api

        app.register_blueprint(views)
        app.register_blueprint(api)

        # Import commands here so they register with the app context
        from .commands import books

        # from .commands import test

        return app


# # --- Database Initialization Command ---
# @app.cli.command('init-db')
# def init_db_command():
#     """Creates the database tables based on models."""
#     # Use app_context to ensure SQLAlchemy has the app configuration
#     with app.app_context():
#         try:
#             db.create_all()
#             print('Initialized the database and created tables.')
#         except Exception as e:
#             print(f'Error initializing database: {e}')
#             # Optionally re-raise or exit
#             exit(1)
# # --- End Database Initialization Command ---
