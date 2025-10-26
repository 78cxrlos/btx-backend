from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import ContactMessage
from flask_jwt_extended import jwt_required

contacts_bp = Blueprint("contacts", __name__)

@contacts_bp.route("", methods=["POST"])
def create_contact():
    data = request.get_json() or {}

    # Accept either separate first/last name fields or a single 'name' for compatibility
    first_name = data.get("first_name") or data.get("firstName") or None
    last_name = data.get("last_name") or data.get("lastName") or None
    name = data.get("name") or None

    email = data.get("email")
    message = data.get("message")

    # Validate
    if not email or not message:
        return jsonify({"msg": "email and message required"}), 400

    cm = ContactMessage(
        first_name=first_name,
        last_name=last_name,
        name=name,
        email=email,
        message=message,
    )
    db.session.add(cm)
    db.session.commit()
    return jsonify({"msg": "message saved", "id": cm.id}), 201

@contacts_bp.route("/admin/", methods=["GET"])  # admin-only view
@jwt_required()
def list_contacts():
    qs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    out = [
        {
            "id": c.id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "name": c.name,
            "display_name": c.display_name(),
            "email": c.email,
            "message": c.message,
            "created_at": c.created_at.isoformat(),
        } for c in qs
    ]
    return jsonify(out), 200
