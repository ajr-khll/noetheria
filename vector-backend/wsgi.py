"""
WSGI entry point for production deployment
"""
import os
from app import app

if __name__ == "__main__":
    # Railway automatically sets PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)