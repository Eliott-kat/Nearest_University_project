"""
Authentication routes for user registration and login
"""
import uuid
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app import app, db
from models import User, UserRole
from auth_forms import RegistrationForm, LoginForm

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth_local.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Create blueprint for auth routes  
auth_bp = Blueprint('auth_local', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user_id = str(uuid.uuid4())
            password_hash = generate_password_hash(form.password.data)
            
            user = User()
            user.id = user_id
            user.email = form.email.data.lower().strip()
            user.first_name = form.first_name.data.strip()
            user.last_name = form.last_name.data.strip()
            user.password_hash = password_hash
            user.role = UserRole(form.role.data)
            
            db.session.add(user)
            db.session.commit()
            
            logging.info(f"Nouvel utilisateur créé: {user.email} ({user.role.value})")
            flash(f'Compte créé avec succès ! Bienvenue {user.first_name} !', 'success')
            
            # Auto-login after registration
            login_user(user)
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erreur création compte: {e}")
            flash('Erreur lors de la création du compte. Veuillez réessayer.', 'danger')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        
        if user and user.password_hash and check_password_hash(user.password_hash, form.password.data):
            if user.active:
                login_user(user, remember=form.remember_me.data)
                logging.info(f"Connexion réussie: {user.email}")
                
                # Redirect to intended page or dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('dashboard'))
            else:
                flash('Votre compte a été désactivé. Contactez l\'administration.', 'warning')
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout current user"""
    user_email = current_user.email
    logout_user()
    logging.info(f"Déconnexion: {user_email}")
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('landing'))

# Blueprint registered in routes.py