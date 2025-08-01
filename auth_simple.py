"""
Système d'authentification simplifié pour AcadCheck
Création de comptes et connexion fonctionnels
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, UserRole, db
from datetime import datetime
import re

# Blueprint pour l'authentification simple
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Récupération des données du formulaire
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        role = request.form.get('role', 'student')
        terms_accepted = request.form.get('terms_accepted')
        
        # Validation des données
        errors = []
        
        if not first_name or len(first_name) < 2:
            errors.append('Le prénom doit contenir au moins 2 caractères')
            
        if not last_name or len(last_name) < 2:
            errors.append('Le nom doit contenir au moins 2 caractères')
            
        if not email or '@' not in email:
            errors.append('Veuillez entrer une adresse email valide')
            
        if not password or len(password) < 8:
            errors.append('Le mot de passe doit contenir au moins 8 caractères')
            
        if password != password_confirm:
            errors.append('Les mots de passe ne correspondent pas')
            
        if not terms_accepted:
            errors.append('Vous devez accepter les conditions d\'utilisation')
            
        # Vérifier si l'email existe déjà
        if email and User.query.filter_by(email=email).first():
            errors.append('Cette adresse email est déjà utilisée')
            
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register_simple.html', 
                                 first_name=first_name,
                                 last_name=last_name,
                                 email=email,
                                 role=role)
        
        # Création du compte
        try:
            user = User()
            user.id = f"{email.split('@')[0]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            user.first_name = first_name.title()
            user.last_name = last_name.title()
            user.email = email
            user.password_hash = generate_password_hash(password)
            user.role = UserRole.PROFESSOR if role == 'professor' else UserRole.STUDENT
            user.active = True
            user.created_at = datetime.now()
            user.updated_at = datetime.now()
            
            db.session.add(user)
            db.session.commit()
            
            # Connexion automatique
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = f"{user.first_name} {user.last_name}"
            session['user_role'] = user.role.value
            
            flash(f'Compte créé avec succès ! Bienvenue {user.first_name} !', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la création du compte. Veuillez réessayer.', 'danger')
            return render_template('auth/register_simple.html')
    
    return render_template('auth/register_simple.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me')
        
        if not email or not password:
            flash('Veuillez remplir tous les champs', 'danger')
            return render_template('auth/login_simple.html', email=email)
        
        # Recherche de l'utilisateur
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email ou mot de passe incorrect', 'danger')
            return render_template('auth/login_simple.html', email=email)
        
        if not user.password_hash:
            flash('Compte non configuré. Veuillez créer un nouveau compte.', 'danger')
            return render_template('auth/login_simple.html', email=email)
        
        if not check_password_hash(user.password_hash, password):
            flash('Email ou mot de passe incorrect', 'danger')
            return render_template('auth/login_simple.html', email=email)
        
        if not user.active:
            flash('Votre compte a été désactivé. Contactez l\'administrateur.', 'danger')
            return render_template('auth/login_simple.html', email=email)
        
        # Connexion réussie
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = f"{user.first_name} {user.last_name}"
        session['user_role'] = user.role.value
        
        # Mise à jour de la dernière connexion
        user.updated_at = datetime.now()
        db.session.commit()
        
        flash(f'Connexion réussie ! Bienvenue {user.first_name} !', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('auth/login_simple.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté avec succès', 'info')
    return redirect(url_for('index'))

def is_logged_in():
    """Vérifie si l'utilisateur est connecté"""
    return 'user_id' in session

def get_current_user():
    """Récupère l'utilisateur actuel"""
    if is_logged_in():
        return User.query.get(session['user_id'])
    return None

def require_auth(f):
    """Décorateur pour protéger les routes"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            flash('Vous devez être connecté pour accéder à cette page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function