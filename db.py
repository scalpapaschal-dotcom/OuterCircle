import os
import atexit
from dotenv import load_dotenv
from psycopg2 import pool

# Load environment variables from .env file
load_dotenv()

class Database:
    """Singleton class to manage the database connection pool."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating the connection pool...")
            cls._instance = super(Database, cls).__new__(cls)
            try:
                cls._instance.connection_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10, # Adjust maxconn based on your application's needs
                    host=os.environ.get('DB_HOST'),
                    port=os.environ.get('DB_PORT'),
                    dbname=os.environ.get('DB_NAME'),
                    user=os.environ.get('DB_USER'),
                    password=os.environ.get('DB_PASSWORD')
                )
            except Exception as e:
                print(f"Error creating connection pool: {e}")
                cls._instance = None
                raise

            # Register a cleanup function to close the pool on exit
            atexit.register(cls._instance.close_all_connections)
        return cls._instance

    def close_all_connections(self):
        if self.connection_pool:
            print("Closing all database connections.")
            self.connection_pool.closeall()