from core.config import configs
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from core.messages import messages

# Base class for all database models
Base = declarative_base()

class Database:
    """
    Database class to manage the database connection and session.
    - Initializes the database engine using the connection URI from the configuration.
    - Provides methods to create and manage database sessions.
    """
    def __init__(self):
        # Create an asynchronous database engine
        self.engine = create_async_engine(configs.DATABASE_URI)  # Add `echo=True` for SQL query logging during debugging.
        self.session = async_sessionmaker(bind=self.engine, expire_on_commit=False)
        print(messages.DB_CONNECTION_SUCCESS)

    def create_session(self) -> AsyncSession:
        """
        Creates a new database session.
        Returns:
        - AsyncSession: A new database session instance.
        """
        return self.session()

    @classmethod
    async def get_db_connection(cls) -> AsyncSession:
        """
        Class method to get a new database session.
        Returns:
        - AsyncSession: A new database session instance.
        """
        return cls().create_session()

    async def get_db(self):
        """
        Dependency for FastAPI to provide a database session.
        - Ensures proper session management using a context manager.
        """
        async with self.session() as session:
            yield session

# Create a global instance of the Database class
connection = Database()