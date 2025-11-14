from waitress import serve
from app import app # Import your Flask app instance
import os
from dal import messages_dal as dal # Import our new Data Access Layer

if __name__ == '__main__':
    # Initialize the database; this creates the tables if they don't exist.
    # It's safe to run this every time the server starts.
    print("Initializing database...")
    dal.init_db_tables()
    # The port is set by the hosting environment (e.g., Render)
    port = int(os.environ.get('PORT', 5000))
    print("Waitress serving your Flask app...")
    serve(app, host='0.0.0.0', port=port)