from flask import Blueprint, current_app, request
from flask_app.modules.extensions import db

views = Blueprint("views", __name__)


@views.route("/")
def hello():
    return "Hello, Flask with SQLAlchemy is running in Docker!"


@views.route("/audiobooks", methods=["GET"])
def get_audiobooks():
    """Fetches all audiobooks from the database using SQLAlchemy."""
    try:
        # Use SQLAlchemy 2.0 style query
        audiobooks_from_db = (
            db.session.execute(db.select(Audiobook).order_by(Audiobook.id))
            .scalars()
            .all()
        )

        # Convert model instances to dictionaries using the method defined in the model
        audiobooks_list = [book.to_dict() for book in audiobooks_from_db]

        return jsonify(audiobooks_list), 200
    except Exception as e:
        # Log the error for better debugging
        app.logger.error(f"Error fetching audiobooks: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "error": "An internal server error occurred while fetching audiobooks."
                }
            ),
            500,
        )
    # Flask-SQLAlchemy handles session management automatically per request
