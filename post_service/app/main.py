from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.database import Database as db, Base
from routes.route import router as api_router
from fastapi.staticfiles import StaticFiles
import os

# Dynamically import all models
def import_all_models():
    """
    Dynamically imports all models to ensure they are registered with SQLAlchemy.
    This is necessary for creating tables and managing ORM mappings.
    """
    import models.post

# Properly scoped async context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    - Initializes the database connection.
    - Dynamically imports models and creates tables if they don't exist.
    - Cleans up the database connection on shutdown.
    """
    # Initialize database connection here
    db_client = db()

    # Import all models to register them with SQLAlchemy
    import_all_models()

    try:
        # Use the engine to create tables (if they don't exist)
        async with db_client.engine.begin() as conn:  # Use the engine, not the session, for DDL
            await conn.run_sync(Base.metadata.create_all)
        yield
    finally:
        # Shutdown: Clean up DB connection if needed
        await db_client.engine.dispose()
    print("Shutting down...")

class Server:
    """
    Server class to encapsulate the FastAPI application setup.
    - Configures the application title, version, and lifespan.
    - Includes API routes and mounts static files.
    """
    def __init__(self):
        # Initialize the FastAPI application with metadata and lifespan
        self.app = FastAPI(
            title="FastAPI",
            version="0.0.1",
            lifespan=lifespan
        )   

        # Use the absolute path to the 'public' directory inside the Docker container
        public_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

        # Mount the 'public' directory to serve static files
        self.app.mount("/public", StaticFiles(directory=public_dir), name="public")

        # Define a root endpoint to verify the service is running
        @self.app.get("/")
        async def read_root():
            """
            Root endpoint to verify that the post service is running.
            """
            return "Post service is running!"
        
        # Include all API routes under the "/api" prefix
        self.app.include_router(api_router, prefix="/api", tags=["api"])
        
# Create an instance of the Server class and expose the FastAPI app
server = Server()
app = server.app