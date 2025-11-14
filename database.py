import os
import psycopg2
from flask import g
from psycopg2.extras import DictCursor

# --- Database Connection ---

# Get the database connection URL from the environment variables.
# This is crucial for services like Render where connection details are not hardcoded.
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """
    Establishes a new connection to the database if one doesn't exist for the current request.
    The connection is stored in Flask's 'g' object, which is unique for each request.
    """
    if 'db_conn' not in g:
        try:
            g.db_conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
        except psycopg2.OperationalError as e:
            print(f"Error connecting to the database: {e}")
            raise
    return g.db_conn

def close_db_connection(e=None):
    """Closes the database connection at the end of the request."""
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

def init_db():
    """
    Initializes the database by creating the necessary tables if they don't already exist.
    This function is called once when the application starts.
    """
    # This function should manage its own connection since it's run outside the app context.
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            # Create the 'users' table to store unique codes.
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_code VARCHAR(4) PRIMARY KEY,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            # Create the 'messages' table.
            cur.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    user_code VARCHAR(4) REFERENCES users(user_code) ON DELETE CASCADE,
                    message TEXT NOT NULL,
                    sensitivity VARCHAR(50),
                    delivery VARCHAR(50),
                    timestamp_utc TIMESTAMP WITH TIME ZONE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            ''')
        conn.commit()
        print("Database initialized successfully.")
    finally:
        if conn:
            conn.close()

# --- Database Interaction Functions ---

def code_exists(code):
    """Checks if a user code already exists in the database."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM users WHERE user_code = %s;", (code,))
        exists = cur.fetchone() is not None
    return exists

def create_user(user_code):
    """Adds a new user with their unique code to the database."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO users (user_code) VALUES (%s);", (user_code.upper(),))
    conn.commit()

def add_message_for_code(code, message_data):
    """Adds a new message for a given user code."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO messages (user_code, message, sensitivity, delivery, timestamp_utc)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (
                code.upper(),
                message_data['message'],
                message_data['sensitivity'],
                message_data['delivery'],
                message_data['timestamp_utc']
            )
        )
    conn.commit()

def get_all_messages_grouped():
    """
    Retrieves all messages from the database, ordered by user and then by time.
    The admin_view.html template will handle the grouping.
    """
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Fetch all messages, ordering by user_code and then by the timestamp
        # to ensure messages from the same user are together and in order.
        cur.execute(
            "SELECT id, user_code, message, sensitivity, delivery, TO_CHAR(timestamp_utc, 'YYYY-MM-DD HH24:MI:SS') as timestamp_utc FROM messages ORDER BY user_code, timestamp_utc DESC;"
        )
        messages = cur.fetchall()
    # The result is a list of dictionary-like objects, e.g., [{'user_code': 'ABCD', 'message': 'Hi', ...}]
    return messages

def delete_message_by_id(message_id):
    """Deletes a specific message from the database by its ID."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM messages WHERE id = %s;", (message_id,))
    conn.commit()
