"""
Simplified authentication system for local installation
"""

# Authentication functions for local development
def require_login(f):
    """Authentication decorator for local development"""
    return f

def make_auth_blueprint():
    """Authentication blueprint function for local development"""
    return None