from flask import Blueprint, jsonify, request, abort, current_app
from flask_app.models import Audiobook, Category, Author
from flask_app.modules.extensions import db
from sqlalchemy import or_, func
import random

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/categories", methods=["GET"])
def get_categories():
    """Get all categories."""
    categories = Category.query.order_by(Category.sort_order).all()
    return jsonify({
        "categories": [category.to_dict() for category in categories],
        "total": len(categories)
    })

@api.route("/categories/<int:category_id>", methods=["GET"])
def get_category_audiobooks(category_id):
    """Get a category and its audiobooks with pagination."""
    # Get pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    
    # Limit per_page to reasonable values
    per_page = min(max(per_page, 1), 50)
    
    # Get the category
    category = Category.query.get_or_404(category_id)
    
    # Get paginated audiobooks for this category
    audiobooks_query = category.audiobooks
    total = audiobooks_query.count()
    audiobooks_paginated = audiobooks_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "category": category.to_dict(),
        "audiobooks": [audiobook.to_dict() for audiobook in audiobooks_paginated.items],
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": audiobooks_paginated.pages,
            "has_next": audiobooks_paginated.has_next
        }
    })

@api.route("/audiobooks/search", methods=["GET"])
def search_audiobooks():
    """Search audiobooks by title, description, or author name."""
    # Get search query and pagination parameters
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    
    # Limit per_page to reasonable values
    per_page = min(max(per_page, 1), 50)
    
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    # Create search filter
    search_term = f"%{query}%"
    search_filter = or_(
        Audiobook.title.ilike(search_term),
        Audiobook.description.ilike(search_term),
        Author.name.ilike(search_term)
    )
    
    # Query audiobooks with join to authors
    audiobooks_query = Audiobook.query.join(
        Audiobook.author, isouter=True
    ).filter(search_filter)
    
    # Get total count and paginate results
    total = audiobooks_query.count()
    audiobooks_paginated = audiobooks_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "audiobooks": [audiobook.to_dict() for audiobook in audiobooks_paginated.items],
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": audiobooks_paginated.pages,
            "has_next": audiobooks_paginated.has_next
        },
        "query": query
    })

@api.route("/audiobooks/<int:audiobook_id>", methods=["GET"])
def get_audiobook(audiobook_id):
    """Get details for a specific audiobook."""
    audiobook = Audiobook.query.get_or_404(audiobook_id)
    return jsonify(audiobook.to_dict())

@api.route("/audiobooks/random", methods=["GET"])
def get_random_audiobooks():
    """Get random audiobooks."""
    number = request.args.get("number", 5, type=int)
    # Limit number to reasonable values
    number = min(max(number, 1), 20)
    
    # Get total count of audiobooks
    total_audiobooks = Audiobook.query.count()
    
    if total_audiobooks == 0:
        return jsonify({"audiobooks": [], "total": 0})
    
    # If we have fewer audiobooks than requested, return all of them
    if total_audiobooks <= number:
        audiobooks = Audiobook.query.all()
        return jsonify({
            "audiobooks": [audiobook.to_dict() for audiobook in audiobooks],
            "total": len(audiobooks)
        })
    
    # Get random audiobooks using SQL's random() function
    audiobooks = Audiobook.query.order_by(func.random()).limit(number).all()
    
    return jsonify({
        "audiobooks": [audiobook.to_dict() for audiobook in audiobooks],
        "total": len(audiobooks)
    })

@api.route("/audiobooks", methods=["GET"])
def get_all_audiobooks():
    """Get all audiobooks with pagination, ordered randomly."""
    # Get pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)
    
    # Limit per_page to reasonable values
    per_page = min(max(per_page, 1), 50)
    
    # Get total count of audiobooks
    total_audiobooks = Audiobook.query.count()
    
    if total_audiobooks == 0:
        return jsonify({
            "audiobooks": [],
            "pagination": {
                "total": 0,
                "page": page,
                "per_page": per_page,
                "pages": 0,
                "has_next": False
            }
        })
    
    # Get paginated audiobooks ordered randomly
    audiobooks_paginated = Audiobook.query.order_by(func.random()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        "audiobooks": [audiobook.to_dict() for audiobook in audiobooks_paginated.items],
        "pagination": {
            "total": total_audiobooks,
            "page": page,
            "per_page": per_page,
            "pages": audiobooks_paginated.pages,
            "has_next": audiobooks_paginated.has_next
        }
    })

@api.route("/audiobooks/count", methods=["GET"])
def get_audiobook_count():
    """Get the total number of audiobooks in the database."""
    try:
        count = Audiobook.query.count()
        return jsonify({"count": count})
    except Exception as e:
        current_app.logger.error(f"Error getting audiobook count: {str(e)}")
        return jsonify({"error": "Failed to get audiobook count"}), 500

# Error handlers
@api.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@api.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500
