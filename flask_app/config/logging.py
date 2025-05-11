"""
Configure logging for the application.
This module sets up logging configuration to reduce verbosity.
"""

import logging
from flask import Flask

def configure_logging(app: Flask):
    """
    Configure logging for the Flask application.
    Reduces verbosity of SQLAlchemy and other components.
    
    Args:
        app: The Flask application instance
    """
    # Set SQLAlchemy loggers to WARNING level
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)
    
    # Set PostgreSQL driver logging to WARNING
    logging.getLogger('psycopg2').setLevel(logging.WARNING)
    
    # Set Flask and Werkzeug logging to WARNING
    logging.getLogger('flask').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    # Configure root logger
    logging.basicConfig(level=logging.WARNING)
    
    # Log that logging has been configured
    app.logger.info("Application logging configured")
