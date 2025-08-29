"""
Authentication forms for AcadCheck
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User, UserRole

class RegistrationForm(FlaskForm):
    first_name = StringField('First name', validators=[
        DataRequired(message='First name is required'),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters')
    ])

    last_name = StringField('Last name', validators=[
        DataRequired(message='Last name is required'),
        Length(min=2, max=50, message='Last name must be between 2 and 50 characters')
    ])

    email = EmailField('Email address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters')
    ])

    password_confirm = PasswordField('Confirm password', validators=[
        DataRequired(message='Password confirmation is required'),
        EqualTo('password', message='Passwords do not match')
    ])

    terms_accepted = BooleanField('I accept the terms of use and privacy policy', validators=[
        DataRequired(message='You must accept the terms of use and privacy policy')
    ])

    submit = SubmitField('Create account')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('This email address is already in use. Please choose another one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email is required')
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])

    remember_me = BooleanField('Remember me')

    submit = SubmitField('Login')