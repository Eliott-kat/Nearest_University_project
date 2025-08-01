#!/usr/bin/env python3
"""
Durcissement sécuritaire pour AcadCheck
Sécurise l'application contre les vulnérabilités communes
"""

import os
import re
import hashlib
import secrets
from functools import wraps
from datetime import datetime, timedelta
import logging

class SecurityHardening:
    """Système de durcissement sécuritaire"""
    
    def __init__(self):
        self.failed_attempts = {}
        self.blocked_ips = {}
        self.rate_limits = {}
        self.suspicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'onload=',
            r'onerror=',
            r'eval\(',
            r'document\.cookie',
            r'SELECT.*FROM.*WHERE',
            r'UNION.*SELECT',
            r'DROP.*TABLE',
            r'INSERT.*INTO',
            r'--\s*$',
            r'/\*.*\*/',
        ]
    
    def sanitize_input(self, text):
        """Nettoie et sécurise les entrées utilisateur"""
        if not text or not isinstance(text, str):
            return ""
        
        # Supprimer les caractères de contrôle
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Échapper les caractères HTML dangereux
        html_escape = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;'
        }
        
        for char, escape in html_escape.items():
            text = text.replace(char, escape)
        
        return text[:10000]  # Limiter la longueur
    
    def detect_malicious_content(self, text):
        """Détecte du contenu malveillant"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logging.warning(f"🚨 Contenu suspect détecté: {pattern}")
                return True
        
        return False
    
    def validate_file_upload(self, file_storage):
        """Valide un fichier uploadé"""
        if not file_storage or not file_storage.filename:
            return False, "Aucun fichier fourni"
        
        filename = file_storage.filename.lower()
        
        # Extensions autorisées
        allowed_extensions = {'.pdf', '.docx', '.txt', '.doc'}
        file_ext = os.path.splitext(filename)[1]
        
        if file_ext not in allowed_extensions:
            return False, f"Extension non autorisée: {file_ext}"
        
        # Vérifier la taille
        file_storage.seek(0, 2)  # Aller à la fin
        size = file_storage.tell()
        file_storage.seek(0)  # Revenir au début
        
        max_size = 16 * 1024 * 1024  # 16MB
        if size > max_size:
            return False, f"Fichier trop volumineux: {size} bytes"
        
        # Vérifier le nom de fichier
        if self.detect_malicious_content(filename):
            return False, "Nom de fichier suspect"
        
        return True, "Fichier valide"
    
    def rate_limit(self, identifier, max_requests=10, window_minutes=1):
        """Limite le taux de requêtes"""
        now = datetime.now()
        window = timedelta(minutes=window_minutes)
        
        # Nettoyer les anciennes entrées
        cutoff = now - window
        self.rate_limits = {
            k: v for k, v in self.rate_limits.items() 
            if v['last_request'] > cutoff
        }
        
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = {
                'count': 1,
                'last_request': now,
                'first_request': now
            }
            return True
        
        entry = self.rate_limits[identifier]
        
        # Si la fenêtre est expirée, réinitialiser
        if now - entry['first_request'] > window:
            entry['count'] = 1
            entry['first_request'] = now
            entry['last_request'] = now
            return True
        
        entry['count'] += 1
        entry['last_request'] = now
        
        if entry['count'] > max_requests:
            logging.warning(f"🚨 Rate limit dépassé pour {identifier}: {entry['count']} requêtes")
            return False
        
        return True
    
    def log_security_event(self, event_type, details, severity="INFO"):
        """Enregistre un événement de sécurité"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[SECURITY] {timestamp} [{severity}] {event_type}: {details}"
        
        if severity == "CRITICAL":
            logging.critical(log_entry)
        elif severity == "WARNING":
            logging.warning(log_entry)
        else:
            logging.info(log_entry)
    
    def generate_secure_token(self, length=32):
        """Génère un token sécurisé"""
        return secrets.token_urlsafe(length)
    
    def hash_password_secure(self, password):
        """Hash un mot de passe de manière sécurisée"""
        from werkzeug.security import generate_password_hash
        return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def validate_password_strength(self, password):
        """Valide la force d'un mot de passe"""
        if not password or len(password) < 8:
            return False, "Mot de passe trop court (minimum 8 caractères)"
        
        checks = {
            'lowercase': re.search(r'[a-z]', password),
            'uppercase': re.search(r'[A-Z]', password),
            'digit': re.search(r'\d', password),
            'special': re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        }
        
        missing = [check for check, found in checks.items() if not found]
        
        if len(missing) > 1:
            return False, f"Mot de passe faible. Manque: {', '.join(missing)}"
        
        # Vérifier les mots de passe communs
        common_passwords = {'password', '123456', 'admin', 'user', 'test'}
        if password.lower() in common_passwords:
            return False, "Mot de passe trop commun"
        
        return True, "Mot de passe valide"

def security_headers(app):
    """Ajoute les en-têtes de sécurité"""
    @app.after_request
    def add_security_headers(response):
        # Prévention du clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Protection XSS
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # HTTPS strict
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # CSP basique
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "font-src 'self' cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
        
        # Référer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    
    return app

def csrf_protection():
    """Protection CSRF basique"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, session, abort
            
            if request.method == 'POST':
                token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
                expected_token = session.get('csrf_token')
                
                if not token or not expected_token or token != expected_token:
                    logging.warning("🚨 Tentative CSRF détectée")
                    abort(403)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Instance globale
security_hardening = SecurityHardening()

def secure_filename(filename):
    """Sécurise un nom de fichier"""
    if not filename:
        return "untitled"
    
    filename = security_hardening.sanitize_input(filename)
    
    # Supprimer les caractères dangereux
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'\.{2,}', '.', filename)  # Pas de .. 
    filename = filename.strip('. ')
    
    if not filename:
        return "untitled"
    
    return filename[:100]  # Limiter la longueur

if __name__ == "__main__":
    # Test du système de sécurité
    print("🔒 TEST DURCISSEMENT SÉCURITAIRE")
    print("-" * 40)
    
    security = SecurityHardening()
    
    # Test détection contenu malveillant
    malicious_tests = [
        "<script>alert('xss')</script>",
        "javascript:alert(1)",
        "SELECT * FROM users WHERE 1=1--",
        "Texte normal et innocent",
        ""
    ]
    
    for test in malicious_tests:
        is_malicious = security.detect_malicious_content(test)
        status = "MALVEILLANT" if is_malicious else "SAIN"
        print(f"   - '{test[:30]}...': {status}")
    
    # Test validation mot de passe
    passwords = [
        "123456",
        "MotDePasse123!",
        "weak",
        "SuperSecurePassword123!@#"
    ]
    
    print("\n🔑 Test validation mots de passe:")
    for pwd in passwords:
        is_valid, message = security.validate_password_strength(pwd)
        status = "VALIDE" if is_valid else "INVALIDE"
        print(f"   - '{pwd}': {status} ({message})")
    
    # Test rate limiting
    print("\n⏱️ Test rate limiting:")
    identifier = "test_user"
    for i in range(12):
        allowed = security.rate_limit(identifier, max_requests=10)
        if not allowed:
            print(f"   - Requête {i+1}: BLOQUÉE")
            break
        else:
            print(f"   - Requête {i+1}: AUTORISÉE")
    
    print("\n✅ Tests de sécurité terminés")