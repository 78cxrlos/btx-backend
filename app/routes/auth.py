from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import AdminUser
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)

# 🧠 Admin Login Only
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400

    # Allow login via username or email
    user = AdminUser.query.filter(
        (AdminUser.username == username) | (AdminUser.email == username)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid credentials"}), 401

    # Create token valid for 8 hours
    access_token = create_access_token(
        identity={"id": user.id, "username": user.username},
        expires_delta=timedelta(hours=8)
    )

    return jsonify({
        "access_token": access_token,
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }), 200


# 🧠 Optional: Get logged-in admin info
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    current_user = get_jwt_identity()
    return jsonify(current_user), 200
