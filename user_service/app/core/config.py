import os
from dotenv import load_dotenv, find_dotenv

# Explicitly load the .env file from the parent of 'app'
env_path = find_dotenv()  # Finds the nearest .env file in the directory hierarchy.

# Load environment variables from the .env file
load_dotenv(dotenv_path=env_path, override=True)

class Config:
    """
    Config class to manage application configuration.
    - Reads environment variables from the .env file.
    - Provides default values if environment variables are not set.
    """
    DATABASE_URI: str = os.getenv("DATABASE_URI", "")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "")
    POST_AUTH_SERVICE_URL: str = os.getenv("POST_AUTH_SERVICE_URL", "")
    POST_SERVICE_URL: str = os.getenv("POST_SERVICE_URL", "")

# Create a global instance of the Config class
configs = Config()