# Import configuration for local development
try:
    import config_local  # Setup environment variables for local installation
except ImportError:
    pass  # config_local.py not found, continue with environment variables

from app import app
import routes  # noqa: F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
