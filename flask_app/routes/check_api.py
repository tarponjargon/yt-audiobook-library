from flask import Blueprint, current_app

check_api = Blueprint("check_api", __name__, url_prefix="/api/check")

@check_api.route("/", methods=["GET"])
def check_api_route():
    """Check if API routes are properly registered."""
    return {"status": "API routes are working"}

# This function should be called in your app's __init__.py
def register_check_api(app):
    app.register_blueprint(check_api)
    current_app.logger.info("Check API routes registered successfully")
