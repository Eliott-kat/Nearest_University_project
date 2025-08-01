# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    # python-dotenv not installed, try config_local fallback
    try:
        import config_local
    except ImportError:
        pass  # No configuration file found, use environment variables

from app import app
import routes  # Import routes to register them
import auth_routes  # Import auth routes

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
