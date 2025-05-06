from pydantic import BaseModel, Field

class BaseUser(BaseModel):
    """
    BaseUser schema to define common fields for user-related operations.
    - `email`: A required field with a regex pattern to validate email format.
    """
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

class UserCreate(BaseUser):
    """
    UserCreate schema for user registration.
    - Inherits `email` from BaseUser.
    - `username`: A required field with a minimum length of 3 and a maximum length of 50.
    - `password`: A required field with a minimum length of 8 and a maximum length of 128.
    """
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)

class UserLogin(BaseUser):
    """
    UserLogin schema for user authentication.
    - Inherits `email` from BaseUser.
    - `password`: A required field with a minimum length of 8 and a maximum length of 128.
    """
    password: str = Field(..., min_length=8, max_length=128)