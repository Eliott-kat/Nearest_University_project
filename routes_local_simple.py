"""
Routes supplémentaires pour l'installation locale
"""
from flask import redirect, url_for
from app import app

@app.route('/logout')
def logout():
    """Route de déconnexion simplifiée pour installation locale"""
    return redirect(url_for('index'))

@app.route('/login')  
def login():
    """Route de connexion simplifiée pour installation locale"""
    return redirect(url_for('index'))