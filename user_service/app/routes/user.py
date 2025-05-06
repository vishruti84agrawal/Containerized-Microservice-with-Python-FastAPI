from fastapi import APIRouter, Depends, Query, Header
from core.response import BaseResponse
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import connection
from middlewares.authentication import check_is_admin, authorize_user
from controller.user import UserController
from typing import Optional
from core.messages import messages

# Create an APIRouter instance for user-related routes
router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# Descriptions for query parameters
USER_ID_QUERY_PARAM_DESC = "ID of user"  # Description for the `user_id` query parameter
USER_EMAIL_QUERY_PARAM_DESC = "User email"  # Description for the `email` query parameter

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

@router.get("/", response_model=BaseResponse, dependencies=[Depends(check_is_admin)])
async def get_users(db: AsyncSession = Depends(get_db)):
    """
    Endpoint to fetch all users.
    - Requires admin privileges (validated by the `check_is_admin` dependency).
    - Calls the UserController to retrieve all users from the database.

    Args:
    - db (AsyncSession): The database session dependency.

    Returns:
    - BaseResponse: A response containing the list of all users or an appropriate error message.
    """
    return await user_controller.get_all_users(db)

@router.get("/detail", response_model=BaseResponse, dependencies=[Depends(authorize_user)])
async def get_user_detail(
    authorization: str = Header(...),
    user_id: Optional[int] = Query(description=USER_ID_QUERY_PARAM_DESC, default=None),
    email: Optional[str] = Query(description=USER_EMAIL_QUERY_PARAM_DESC, default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to fetch user details by ID or email.
    - Requires user authorization (validated by the `authorize_user` dependency).
    - Accepts either `user_id` or `email` as a query parameter to identify the user.
    - Calls the UserController to retrieve the user details from the database.

    Workflow:
    1. Extracts the JWT token from the Authorization header.
    2. Validates that either `user_id` or `email` is provided.
    3. Calls the UserController to fetch the user details.
    4. Calls Post Service via nginx to fetch posts created by the user (if applicable).

    Args:
    - authorization (str): The Authorization header containing the JWT token.
    - user_id (Optional[int]): The ID of the user to fetch.
    - email (Optional[str]): The email of the user to fetch.
    - db (AsyncSession): The database session dependency.

    Returns:
    - BaseResponse: A response containing the user details or an appropriate error message.
    """
    # Extract the token from the Authorization header
    token = authorization.replace("Bearer ", "")

    # Validate that either `user_id` or `email` is provided
    if not user_id and not email:
        return BaseResponse(
            resp_code=400,
            message=messages.USER_ID_EMAIL_REQUIRED,
        )

    # Fetch user details using the UserController
    return await user_controller.get_user_by_column(db, user_id, email, False, token)