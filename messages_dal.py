from db import Database

def add_message(name, email, message):
    """
    Inserts a new message into the database.
    Uses a connection from the pool.
    """
    # SQL query with placeholders to prevent SQL injection
    sql = "INSERT INTO messages (name, email, message) VALUES (%s, %s, %s) RETURNING id;"
    conn = None
    try:
        # Get a connection from the pool
        db = Database()
        conn = db.connection_pool.getconn()
        with conn.cursor() as cursor:
            # Execute the query safely with parameters
            cursor.execute(sql, (name, email, message))
            new_id = cursor.fetchone()[0]
            conn.commit() # Commit the transaction
            print(f"Successfully inserted message with ID: {new_id}")
            return new_id
    except Exception as e:
        print(f"Error adding message to database: {e}")
        if conn:
            conn.rollback() # Rollback on error
        return None
    finally:
        # Return the connection to the pool
        if conn:
            db.connection_pool.putconn(conn)

# You can add more functions here as needed, for example:
# def get_all_messages():
# def get_message_by_id(id):