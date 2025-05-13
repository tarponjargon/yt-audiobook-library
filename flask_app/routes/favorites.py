from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from flask_app.models import Audiobook, db

favorites = Blueprint("favorites", __name__, url_prefix="/api/favorites")

@favorites.route("/", methods=["GET"])
@login_required
def get_favorites():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    favorites_query = current_user.favorites
    paginated = favorites_query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        "audiobooks": [book.to_dict() for book in paginated.items],
        "pagination": {
            "page": paginated.page,
            "per_page": paginated.per_page,
            "total": paginated.total,
            "pages": paginated.pages,
            "has_next": paginated.has_next,
            "has_prev": paginated.has_prev
        }
    })

@favorites.route("/<int:audiobook_id>", methods=["POST"])
@login_required
def add_favorite(audiobook_id):
    audiobook = Audiobook.query.get_or_404(audiobook_id)
    
    if audiobook in current_user.favorites.all():
        return jsonify({"message": "Audiobook already in favorites"}), 400
    
    current_user.favorites.append(audiobook)
    db.session.commit()
    
    return jsonify({"message": "Audiobook added to favorites"})

@favorites.route("/<int:audiobook_id>", methods=["DELETE"])
@login_required
def remove_favorite(audiobook_id):
    audiobook = Audiobook.query.get_or_404(audiobook_id)
    
    if audiobook not in current_user.favorites.all():
        return jsonify({"message": "Audiobook not in favorites"}), 400
    
    current_user.favorites.remove(audiobook)
    db.session.commit()
    
    return jsonify({"message": "Audiobook removed from favorites"})

@favorites.route("/check/<int:audiobook_id>", methods=["GET"])
@login_required
def check_favorite(audiobook_id):
    audiobook = Audiobook.query.get_or_404(audiobook_id)
    is_favorite = audiobook in current_user.favorites.all()
    
    return jsonify({"is_favorite": is_favorite})
