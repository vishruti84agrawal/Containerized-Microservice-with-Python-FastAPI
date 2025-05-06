from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schema.user import UserCreate, UserLogin
from core.response import BaseResponse
from core.messages import messages
from utils.secret import SecretManager
from typing import Optional
from utils.jwt import JWTManager
import httpx
from core.config import configs
from fastapi import status

class UserController:
    """
    UserController handles all user-related operations, such as creating users,
    fetching user details, and validating user credentials.
    """

    @staticmethod
    def serialize_user(user: User) -> dict:
        """
        Serializes a User object into a dictionary.
        Args:
        - user (User): The User object to serialize.

        Returns:
        - dict: A dictionary representation of the User object.
        """
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password": user.password,
            "is_admin": user.is_admin
        }

    async def create_user(self, db: AsyncSession, schema: UserCreate) -> BaseResponse:
        """
        Creates a new user in the database.
        Args:
        - db (AsyncSession): The database session.
        - schema (UserCreate): The user creation schema.

        Returns:
        - BaseResponse: A response indicating success or failure.
        """
        try:
            # Check if user already exists
            result = await db.execute(select(User).where(User.email == schema.email))
            existing_user = result.scalar_one_or_none()
            secret_util = SecretManager()

            if existing_user:
                return BaseResponse(
                    resp_code=400,
                    message=messages.USER_ALREADY_EXISTS,
                )
            else:
                # Create a new user
                user = User(
                    username=schema.username,
                    email=schema.email,
                    password=secret_util.hash_password(schema.password),
                )

                db.add(user)
                await db.commit()
                await db.refresh(user)
                return BaseResponse(
                    resp_code=201,
                    message=messages.USER_CREATION_SUCCESS,
                )
        except Exception as e:
            db.rollback()
            return BaseResponse(
                resp_code=500,
                message=str(e),
            )
        finally:
            db.close()

    async def fetch_user_for_login(self, db: AsyncSession, schema: UserLogin) -> BaseResponse:
        """
        Fetches user details for login and validates credentials.
        Args:
        - db (AsyncSession): The database session.
        - schema (UserLogin): The user login schema.

        Returns:
        - BaseResponse: A response containing user details or an error message.
        """
        try:
            if not schema.email:
                return BaseResponse(
                    resp_code=400,
                    message=messages.EMAIL_REQUIRED,
                )
            elif not schema.password:
                return BaseResponse(
                    resp_code=400,
                    message=messages.PASSWORD_REQUIRED,
                )

            # Check if user exists
            user = await UserController.get_user_by_column(self, db, None, schema.email)

            if user.resp_code == 404:
                return BaseResponse(
                    resp_code=404,
                    message=messages.INVALID_CREDENTIALS,
                )

            secret_util = SecretManager()

            if secret_util.verify_password(schema.password, user.data['password']):
                del user.data['password']  # Remove password from the response

                # Generate JWT token
                jwt_util = JWTManager()
                token = jwt_util.create_access_token(data=user.data)
                user.data['token'] = token

                return BaseResponse(
                    resp_code=200,
                    message=messages.USER_SIGN_IN_SUCCESS,
                    data=user.data
                )
            else:
                return BaseResponse(
                    resp_code=401,
                    message=messages.INVALID_CREDENTIALS,
                )
        except Exception as e:
            db.rollback()
            return BaseResponse(
                resp_code=500,
                message=str(e),
            )
        finally:
            db.close()

    async def get_user_by_column(self, db: AsyncSession, id: Optional[int] = None, email: Optional[str] = None, is_password: bool = True, token: Optional[str] = None) -> BaseResponse:
        """
        Fetches user details by ID or email.
        Args:
        - db (AsyncSession): The database session.
        - id (Optional[int]): The user ID.
        - email (Optional[str]): The user email.
        - is_password (bool): Whether to include the password in the response.
        - token (Optional[str]): The authorization token.

        Returns:
        - BaseResponse: A response containing user details or an error message.
        """
        try:
            stmt = select(User)

            if id:
                stmt = stmt.where(User.id == id)
            elif email:
                stmt = stmt.where(User.email == email)

            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                if not is_password:
                    user_data = {key: value for key, value in UserController.serialize_user(user).items() if key != "password"}

                    # Fetch posts for the user via nginx
                    user_posts = await UserController.get_user_posts(id, token)

                    if user_posts['resp_code'] == 200:
                        user_data['posts'] = user_posts['data']
                    else:
                        user_data['posts'] = []

                    return BaseResponse(
                        resp_code=200,
                        message=messages.USER_DETAILS_SUCCESS,
                        data=user_data
                    )
                else:
                    return BaseResponse(
                        resp_code=200,
                        message=messages.USER_DETAILS_SUCCESS,
                        data=UserController.serialize_user(user)
                    )
            else:
                return BaseResponse(
                    resp_code=404,
                    message=messages.USER_NOT_FOUND,
                )
        except Exception as e:
            return BaseResponse(
                resp_code=500,
                message=str(e),
            )
        finally:
            db.close()

    async def get_all_users(self, db: AsyncSession) -> BaseResponse:
        """
        Fetches all users from the database.
        Args:
        - db (AsyncSession): The database session.

        Returns:
        - BaseResponse: A response containing the list of users or an error message.
        """
        try:
            result = await db.execute(select(User))
            users = result.scalars().all()

            if users:
                sanitized_users = [
                    {key: value for key, value in UserController.serialize_user(user).items() if key != "password"}
                    for user in users
                ]

                return BaseResponse(
                    resp_code=200,
                    message=messages.USER_LIST_SUCCESS,
                    data=sanitized_users
                )
            else:
                return BaseResponse(
                    resp_code=404,
                    message=messages.USER_LIST_EMPTY,
                )
        except Exception as e:
            return BaseResponse(
                resp_code=500,
                message=str(e),
            )
        finally:
            db.close()

    async def get_user_posts(self, user_id: int, token: str):
        """
        Fetches posts created by a user by communicating with the post service via nginx.
        Args:
        - user_id (int): The ID of the user.
        - token (str): The authorization token.

        Returns:
        - dict: A response containing the user's posts or an error message.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{configs.POST_SERVICE_URL}/user-posts?user_id={user_id}", headers={"Authorization": token})

                response_data = response.json()

                if response_data and response_data.get("resp_code") != 200:
                    return BaseResponse(
                        resp_code=status.HTTP_401_UNAUTHORIZED,
                        message=response_data.get("message"),
                    )
                else:
                    return response.json()
        except Exception as e:
            return BaseResponse(
                resp_code=500,
                message=str(e),
            )