import os
from dotenv import load_dotenv
import database as db

# Load environment variables from a .env file if it exists.
# This is useful for local development.
load_dotenv()

print("Attempting to initialize the database...")
if not os.environ.get('DATABASE_URL'):
    print("ERROR: DATABASE_URL environment variable not set. Cannot initialize database.")
else:
    db.init_db()
    print("Database initialization script finished.")