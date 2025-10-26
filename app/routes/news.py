import os
from flask import Blueprint, request, jsonify, current_app, url_for
from ..extensions import db
from ..models import NewsArticle
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime
import math
import re
from flask_cors import cross_origin

ALLOWED_EXTENSIONS = {"pdf"}

news_bp = Blueprint("news", __name__)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def estimate_read_time_minutes(text: str) -> int:
    if not text:
        return 1
    # crude word count
    words = len(re.findall(r"\w+", text))
    # assume 200 wpm reading speed
    minutes = max(1, math.ceil(words / 200))
    return minutes

@news_bp.route("/", methods=["GET"])
@news_bp.route("", methods=["GET"])
def list_news():
    qs = NewsArticle.query.order_by(NewsArticle.created_at.desc()).all()
    out = []
    for n in qs:
        pdf_url = None
        is_pdf = False
        if n.pdf_filename:
            pdf_url = url_for("uploaded_file", filename=n.pdf_filename, _external=True)
            is_pdf = True

        # date: frontend expects `date` and `readTime`
        out.append({
            "id": n.id,
            "title": n.title,
            "excerpt": n.excerpt,
            "content": n.content,
            # return ISO date string in `date` field (frontend will format)
            "date": n.created_at.isoformat(),
            # readTime like "3 min read"
            "readTime": f"{(n.read_time or estimate_read_time_minutes(n.content))} min read",
            "category": n.category,
            "isPdf": is_pdf,
            "pdfUrl": pdf_url,
            "slug": n.slug
        })
    return jsonify(out), 200

@news_bp.route("/admin", methods=["POST"])
@jwt_required()
def create_news():
    # expecting multipart/form-data for possible file upload
    title = request.form.get("title")
    excerpt = request.form.get("excerpt")
    content = request.form.get("content")
    category = request.form.get("category")

    if not title:
        return jsonify({"msg": "title is required"}), 400

    pdf_file = request.files.get("pdf")
    pdf_filename = None
    if pdf_file:
        if pdf_file.filename == "":
            return jsonify({"msg": "no selected file"}), 400
        if not allowed_file(pdf_file.filename):
            return jsonify({"msg": "file type not allowed, only pdf"}), 400

        filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{pdf_file.filename}")
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        pdf_file.save(save_path)
        pdf_filename = filename

    # compute read time in minutes
    read_minutes = estimate_read_time_minutes(content)

    article = NewsArticle(
        title=title,
        excerpt=excerpt,
        content=content,
        category=category,
        pdf_filename=pdf_filename,
        read_time=read_minutes
    )
    db.session.add(article)
    db.session.commit()

    pdf_url = None
    is_pdf = False
    if pdf_filename:
        pdf_url = url_for("uploaded_file", filename=pdf_filename, _external=True)
        is_pdf = True

    return jsonify({
        "msg": "article created",
        "article": {
            "id": article.id,
            "title": article.title,
            "excerpt": article.excerpt,
            "content": article.content,
            "category": article.category,
            "pdf_url": pdf_url,
            "isPdf": is_pdf,
            "readTime": f"{article.read_time} min read",
            "date": article.created_at.isoformat(),
            "slug": article.slug
        }
    }), 201

@news_bp.route("/admin/<int:article_id>", methods=["DELETE"])
@jwt_required()
@cross_origin(origin="http://localhost:5173", headers=["Content-Type", "Authorization"])
def delete_news(article_id):
    article = NewsArticle.query.get_or_404(article_id)
    if article.pdf_filename:
        try:
            os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], article.pdf_filename))
        except Exception:
            pass
    db.session.delete(article)
    db.session.commit()
    return jsonify({"msg": "deleted"}), 200
