from waitress import serve
from app import app # Import your Flask app instance
import os
from dotenv import load_dotenv
from dal import messages_dal as dal # Import our new Data Access Layer

# Load environment variables from .env file for local development
load_dotenv()

if __name__ == '__main__':
    # Initialize the database; this creates the tables if they don't exist.
    # It's safe to run this every time the server starts.
    print("Checking database tables...")
    dal.init_db_tables()
    # The port is set by the hosting environment (e.g., Render)
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Waitress server on host 0.0.0.0 port {port}...")
    serve(app, host='0.0.0.0', port=port)