import os
import psycopg2
from psycopg2.extras import DictCursor

# --- Database Connection ---

# Get the database connection URL from the environment variables.
# This is crucial for services like Render where connection details are not hardcoded.
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    Returns a connection object.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
        return conn
    except psycopg2.OperationalError as e:
        # This will help you debug if the DATABASE_URL is wrong or the database is down.
        print(f"Error connecting to the database: {e}")
        raise

def init_db():
    """
    Initializes the database by creating the necessary tables if they don't already exist.
    This function is called once when the application starts.
    """
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Create the 'users' table to store unique codes.
        # The user_code is the primary key, ensuring each is unique.
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_code VARCHAR(4) PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Create the 'messages' table to store all submitted messages.
        # It's linked to the 'users' table via the user_code foreign key.
        # ON DELETE CASCADE means if a user is deleted, all their messages are also deleted.
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
    conn.close()
    print("Database initialized successfully.")

# --- Database Interaction Functions ---

def code_exists(code):
    """Checks if a user code already exists in the database."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM users WHERE user_code = %s;", (code,))
        exists = cur.fetchone() is not None
    conn.close()
    return exists

def create_user(user_code):
    """Adds a new user with their unique code to the database."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO users (user_code) VALUES (%s);", (user_code,))
    conn.commit()
    conn.close()

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
                code,
                message_data['message'],
                message_data['sensitivity'],
                message_data['delivery'],
                message_data['timestamp_utc']
            )
        )
    conn.commit()
    conn.close()

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
            "SELECT user_code, message, sensitivity, delivery, TO_CHAR(timestamp_utc, 'YYYY-MM-DD HH24:MI:SS') as timestamp_utc FROM messages ORDER BY user_code, timestamp_utc DESC;"
        )
        messages = cur.fetchall()
    conn.close()
    # The result is a list of dictionary-like objects, e.g., [{'user_code': 'ABCD', 'message': 'Hi', ...}]
    return messages
