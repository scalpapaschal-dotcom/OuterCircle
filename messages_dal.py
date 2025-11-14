from db import Database
from psycopg2.extras import DictCursor

def _execute_query(sql, params=None, fetch=None):
    """Helper function to execute a query using the connection pool."""
    conn = None
    try:
        db = Database()
        conn = db.connection_pool.getconn()
        # Use DictCursor to get dictionary-like rows
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql, params)
            if fetch == 'one':
                result = cursor.fetchone()
            elif fetch == 'all':
                result = cursor.fetchall()
            else:
                result = None # For INSERT, UPDATE, DELETE without RETURNING
            conn.commit()
            return result
    except Exception as e:
        print(f"Database query failed: {e}")
        if conn:
            conn.rollback()
        # Re-raise the exception to be handled by the caller if needed
        raise
    finally:
        if conn:
            db.connection_pool.putconn(conn)

def code_exists(code):
    """Checks if a user code already exists in the database."""
    sql = "SELECT 1 FROM users WHERE user_code = %s;"
    result = _execute_query(sql, (code,), fetch='one')
    return result is not None

def create_user(user_code):
    """Adds a new user with their unique code to the database."""
    sql = "INSERT INTO users (user_code) VALUES (%s);"
    _execute_query(sql, (user_code.upper(),))

def add_message_for_code(code, message_data):
    """
    Inserts a new message into the database.
    Uses a connection from the pool.
    """
    sql = """
        INSERT INTO messages (user_code, message, sensitivity, delivery, timestamp_utc)
        VALUES (%s, %s, %s, %s, %s) RETURNING id;
    """
    params = (
        code.upper(),
        message_data['message'],
        message_data['sensitivity'],
        message_data['delivery'],
        message_data['timestamp_utc']
    )
    result = _execute_query(sql, params, fetch='one')
    print(f"Successfully inserted message with ID: {result['id']}")
    return result['id']

def get_all_messages_grouped():
    """
    Retrieves all messages from the database, ordered for grouping.
    """
    sql = """
        SELECT id, user_code, message, sensitivity, delivery, 
               TO_CHAR(timestamp_utc, 'YYYY-MM-DD HH24:MI:SS') as timestamp_utc 
        FROM messages 
        ORDER BY user_code, timestamp_utc DESC;
    """
    return _execute_query(sql, fetch='all')

def delete_message_by_id(message_id):
    """Deletes a specific message from the database by its ID."""
    sql = "DELETE FROM messages WHERE id = %s;"
    _execute_query(sql, (message_id,))

def init_db_tables():
    """
    Initializes the database by creating the necessary tables if they don't already exist.
    This function should manage its own connection since it's run outside the app context.
    """
    # This is a simplified version of _execute_query for initialization
    conn = None
    try:
        db = Database()
        conn = db.connection_pool.getconn()
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
        print("Database tables initialized successfully.")
    finally:
        if conn:
            db.connection_pool.putconn(conn)