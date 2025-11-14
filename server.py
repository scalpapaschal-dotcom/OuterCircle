from waitress import serve
from app import app # Import your Flask app instance
import os

if __name__ == '__main__':
    # The port is set by the hosting environment (e.g., Render)
    port = int(os.environ.get('PORT', 5000))
    print("Waitress serving your Flask app...")
    serve(app, host='0.0.0.0', port=port)