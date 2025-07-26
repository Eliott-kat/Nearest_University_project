"""
Simplified auth module for local installation
"""

# Dummy functions to replace Replit auth for local development
def require_login(f):
    """Dummy decorator that bypasses authentication for local development"""
    return f

def make_replit_blueprint():
    """Dummy function that returns None for local development"""
    return None