from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_app.models import User, db

auth = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already exists"}), 400
    
    # Create new user
    user = User(
        email=data.get('email')
    )
    user.set_password(data.get('password'))
    
    db.session.add(user)
    db.session.commit()
    
    # Log the user in
    login_user(user)
    
    return jsonify({"message": "User registered successfully", "user": user.to_dict()}), 201

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
    
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({"message": "Login successful", "user": user.to_dict()})
    
    return jsonify({"error": "Invalid email or password"}), 401

@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"})

@auth.route("/me", methods=["GET"])
@login_required
def get_current_user():
    return jsonify({"user": current_user.to_dict()})
