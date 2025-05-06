from fastapi import APIRouter, Depends, Header, status
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import connection
from schema.user import UserCreate, UserLogin
from core.response import BaseResponse
from controller.user import UserController
from jose import JWTError, jwt  # Dependency for decoding JWT tokens
from core.config import configs
from core.messages import messages

# Create an APIRouter instance for authentication-related routes
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# Instantiate the UserController to handle user-related operations
user_controller = UserController()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get the database session.
    - Opens a new database session for each request.
    - Ensures the session is properly closed after the request is processed.
    """
    async with connection.session() as session:
        try:
            yield session
        finally:
            await session.close()

@router.post("/sign-up", response_model=BaseResponse)
async def register_user(user_details: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to register a new user.
    - Accepts user details (username, email, password).
    - Calls the UserController to create a new user in the database.
    """
    return await user_controller.create_user(db, user_details)

@router.post("/sign-in", response_model=BaseResponse)
async def login_user(user_details: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to log in a user.
    - Accepts user credentials (email, password).
    - Calls the UserController to validate the credentials and generate a JWT token.
    """
    return await user_controller.fetch_user_for_login(db, user_details)

@router.get("/validate-token", response_model=BaseResponse)
async def validate_token(authorization: str = Header(...), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to validate a JWT token for service-to-service communication.
    - This route is used by the `post_service` to verify that the user creating or updating a post is authorized.
    - The token is extracted from the Authorization header.
    - The token is decoded and validated using the secret key and algorithm.

    Workflow:
    1. `post_service` sends a request to this endpoint via NGINX - <NGINX_HOST>:8080/api/auth/validate-token.
    2. The JWT token is validated.
    3. If valid, the user details are returned to `post_service`.
    4. If invalid, an unauthorized response is returned.

    Args:
    - authorization (str): The Authorization header containing the JWT token.
    - db (AsyncSession): The database session dependency.

    Returns:
    - BaseResponse: A response indicating whether the token is valid or not, along with user details if valid.
    """
    token = authorization.replace("Bearer ", "")

    try:
        # Decode the JWT token using the secret key and algorithm
        payload = jwt.decode(token, configs.JWT_SECRET_KEY, algorithms=[configs.ALGORITHM])

        # Check if the user still exists in the database
        user = await user_controller.get_user_by_column(db, payload.get("id"), payload.get("email"))

        if not user or not user.data:
            # Return an unauthorized response if the user does not exist
            return BaseResponse(
                resp_code=status.HTTP_401_UNAUTHORIZED,
                message=messages.UNAUTHORIZED,
            )
        else:
            # Return the decoded token payload if the token is valid
            return BaseResponse(
                resp_code=status.HTTP_200_OK,
                message="",
                data=payload
            )
    except JWTError as jwt_error:
        # Handle JWT decoding errors
        return BaseResponse(
            resp_code=status.HTTP_401_UNAUTHORIZED,
            message=str(jwt_error),
        )