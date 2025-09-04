import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "ma-cle-secrete-super-longue-pour-acadcheck-2025")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///acadcheck.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300, "pool_size": 10, "max_overflow": 20,
    "pool_pre_ping": True,
}

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Copyleaks configuration
app.config['COPYLEAKS_EMAIL'] = os.environ.get('COPYLEAKS_EMAIL', 'your-email@example.com')
app.config['COPYLEAKS_API_KEY'] = os.environ.get('COPYLEAKS_API_KEY', 'your-api-key')


# initialize the app with the extension
db.init_app(app)

# Register authentication blueprint
from auth_simple import auth_bp
app.register_blueprint(auth_bp)

# Branding context (allows dynamic renaming without touching templates)
@app.context_processor
def inject_brand():
    return {"BRAND_NAME": os.environ.get("BRAND_NAME", "NEU-AcadCheck")}

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Create reports directory
reports_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'reports')
os.makedirs(reports_dir, exist_ok=True)
logging.info(f"Created upload directory: {app.config['UPLOAD_FOLDER']}")
logging.info(f"Created reports directory: {reports_dir}")

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    db.create_all()
    logging.info("Database tables created")

# Initialiser le support des langues
import language_utils
language_utils.init_app(app)
