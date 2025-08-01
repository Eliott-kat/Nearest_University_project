"""
Authentication forms for AcadCheck
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User, UserRole

class RegistrationForm(FlaskForm):
    first_name = StringField('Prénom', validators=[
        DataRequired(message='Le prénom est requis'), 
        Length(min=2, max=50, message='Le prénom doit contenir entre 2 et 50 caractères')
    ])
    
    last_name = StringField('Nom', validators=[
        DataRequired(message='Le nom est requis'), 
        Length(min=2, max=50, message='Le nom doit contenir entre 2 et 50 caractères')
    ])
    
    email = EmailField('Email', validators=[
        DataRequired(message='L\'email est requis'), 
        Email(message='Veuillez entrer une adresse email valide')
    ])
    
    password = PasswordField('Mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis'),
        Length(min=8, message='Le mot de passe doit contenir au moins 8 caractères')
    ])
    
    password_confirm = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message='La confirmation du mot de passe est requise'),
        EqualTo('password', message='Les mots de passe ne correspondent pas')
    ])
    
    role = SelectField('Rôle', choices=[
        (UserRole.STUDENT.value, 'Étudiant'),
        (UserRole.PROFESSOR.value, 'Professeur')
    ], default=UserRole.STUDENT.value, validators=[DataRequired()])
    
    terms_accepted = BooleanField('J\'accepte les conditions d\'utilisation', validators=[
        DataRequired(message='Vous devez accepter les conditions d\'utilisation')
    ])
    
    submit = SubmitField('Créer le compte')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Cette adresse email est déjà utilisée. Veuillez en choisir une autre.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis')
    ])
    
    password = PasswordField('Mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis')
    ])
    
    remember_me = BooleanField('Se souvenir de moi')
    
    submit = SubmitField('Se connecter')