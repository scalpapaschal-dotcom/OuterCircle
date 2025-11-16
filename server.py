from waitress import serve
from app import create_app # Import the application factory
import os

if __name__ == '__main__':
    # Create an instance of the app using the factory
    app = create_app()

    # The port is set by the hosting environment (e.g., Render)
    port = int(os.environ.get('PORT', 5000))
    print("Waitress serving your Flask app...")
    serve(app, host='0.0.0.0', port=port)