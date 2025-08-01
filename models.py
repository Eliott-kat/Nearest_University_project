from datetime import datetime
from enum import Enum
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

class UserRole(Enum):
    STUDENT = "student"
    PROFESSOR = "professor"
    ADMIN = "admin"

class DocumentStatus(Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String(256))  # For classic authentication
    profile_image_url = db.Column(db.String, nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    documents = db.relationship('Document', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def __repr__(self):
        return f'<User {self.email}>'

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    extracted_text = db.Column(db.Text)
    
    # Copyleaks integration
    scan_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    
    # User relationship
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    analysis_result = db.relationship('AnalysisResult', backref='document', uselist=False, cascade='all, delete-orphan')

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    
    # Plagiarism results
    plagiarism_score = db.Column(db.Float)  # Percentage
    total_words = db.Column(db.Integer)
    identical_words = db.Column(db.Integer)
    minor_changes_words = db.Column(db.Integer)
    related_meaning_words = db.Column(db.Integer)
    
    # AI detection results
    ai_score = db.Column(db.Float)  # Percentage
    ai_words = db.Column(db.Integer)
    
    # Raw results from APIs
    raw_results = db.Column(db.JSON)
    
    # Additional fields for compatibility
    sources_count = db.Column(db.Integer, default=0)
    analysis_provider = db.Column(db.String(100))
    raw_response = db.Column(db.Text)
    
    # Highlighted text with problematic sentences
    highlighted_text = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class HighlightedSentence(db.Model):
    __tablename__ = 'highlighted_sentences'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    
    sentence_text = db.Column(db.Text, nullable=False)
    start_position = db.Column(db.Integer, nullable=False)
    end_position = db.Column(db.Integer, nullable=False)
    
    # Type of issue
    is_plagiarism = db.Column(db.Boolean, default=False)
    is_ai_generated = db.Column(db.Boolean, default=False)
    
    # Confidence scores
    plagiarism_confidence = db.Column(db.Float)
    ai_confidence = db.Column(db.Float)
    
    # Source information for plagiarism
    source_url = db.Column(db.String(500))
    source_title = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    document = db.relationship('Document', backref='highlighted_sentences')
