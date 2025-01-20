import psycopg2
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.model import Base
from common.environment import get_db_credentials


class DatabaseManager:
    """
    Singleton-like manager to handle database initialization and session handling.
    Ensures database is only initialized once on first import.
    """
    _engine = None
    _SessionLocal = None

    @classmethod
    def create_database(cls):
        """Check if the database exists; if not, create it."""
        user, password = get_db_credentials()
        
        connection_params = {
            "dbname": "postgres",  # Always connect to the default database
            "user": user,
            "password": password,
            "host": "localhost",
            "port": 5432,
        }

        try:
            # Connect explicitly with autocommit to isolate this command
            conn = psycopg2.connect(**connection_params)
            conn.autocommit = True
            cursor = conn.cursor()

            # Check if database already exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'solarflare'")
            if not cursor.fetchone():
                print("Database 'solarflare' does not exist. Creating...")
                cursor.execute("CREATE DATABASE solarflare;")
                print("Database 'solarflare' created.")
            else:
                print("Database 'solarflare' already exists.")
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error while creating database: {e}")
            raise
    
    @classmethod
    def get_engine(cls):
        """Lazy initialize the engine."""
        if cls._engine is None:
            # make sure database exists
            cls.create_database()

            user, password = get_db_credentials()
            db_url = f"postgresql://{user}:{password}@localhost:5432/solarflare"
            cls._engine = create_engine(db_url, echo=True)

            # Ensure the sessionmaker is created here
            cls._SessionLocal = sessionmaker(bind=cls._engine)
            cls.initialize_database()
        return cls._engine

    @classmethod
    def initialize_database(cls):
        """Check if the database tables exist and initialize them if necessary."""
        try:
            print("Initializing database schema...")
            Base.metadata.create_all(bind=cls._engine)
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise

    @classmethod
    @contextmanager
    def session_scope(cls):
        """
        Context manager for database sessions. Automatically commits or rolls back transactions.
        Usage:
            with DatabaseManager.session_scope() as session:
                # perform DB operations
        """
        # Ensure the engine and session are initialized
        if cls._SessionLocal is None:
            cls.get_engine()  # Force initialization

        session = cls._SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            print(f"Exception during session: {e}")
            session.rollback()
            raise
        finally:
            session.close()
