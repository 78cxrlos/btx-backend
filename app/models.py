from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class AdminUser(db.Model):
    __tablename__ = "admin_users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=True)
    last_name = db.Column(db.String(150), nullable=True)
    # Keep a legacy 'name' field optional for compatibility if the frontend ever sends it
    name = db.Column(db.String(300), nullable=True)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def display_name(self):
        if self.first_name or self.last_name:
            return f"{(self.first_name or '').strip()} {(self.last_name or '').strip()}".strip()
        if self.name:
            return self.name
        return ""

class NewsArticle(db.Model):
    __tablename__ = "news_articles"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(400), nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(120), nullable=True)
    pdf_filename = db.Column(db.String(500), nullable=True)
    # store read time in minutes (integer). We'll return a pretty string via the API.
    read_time = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(512), unique=True, default=lambda: str(uuid.uuid4()))
