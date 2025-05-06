from fastapi import APIRouter, Depends, Form, File, UploadFile, Query
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import connection
from core.response import BaseResponse
from middlewares.authorization import verify_token
from uuid import uuid4
import os
from controller.post import PostService
from schema.post import BasePost

# Create an APIRouter instance for post-related routes
router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

# Instantiate the PostService controller to handle post-related operations
post_controller = PostService()

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

@router.get(
    "/",
    response_model=BaseResponse,
    dependencies=[Depends(verify_token)]
)
async def get_post_details(
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to fetch the list of all posts.
    - Requires user authentication (validated by the `verify_token` dependency).
    - Calls the PostService to retrieve the list of posts.

    Args:
    - db (AsyncSession): The database session dependency.

    Returns:
    - BaseResponse: A response containing the list of posts or an error message.
    """
    return await post_controller.get_post_list(db)

@router.post("/create", response_model=BaseResponse, dependencies=[Depends(verify_token)])
async def create_post(
    title: str = Form(...),
    description: str = Form(...),
    post_image: UploadFile = File(None),
    user=Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to create a new post.
    - Requires user authentication (validated by the `verify_token` dependency).
    - Accepts post details (title, description, and optional image).
    - Saves the image to a directory if provided.

    Args:
    - title (str): The title of the post.
    - description (str): The description of the post.
    - post_image (UploadFile): Optional image file for the post.
    - user: The authenticated user details.
    - db (AsyncSession): The database session dependency.

    Returns:
    - BaseResponse: A response indicating success or failure.
    """
    created_by_user_id = user.get('data').get('id')

    # Image storage
    image_url = None

    if post_image and post_image.filename:
        # Validate the file type (optional)
        if not post_image.filename.endswith(('.png', '.jpg', '.jpeg')):
            return BaseResponse(
                resp_code=400,
                message="Invalid file type. Only PNG, JPG, and JPEG are allowed.",
                data={}
            )

        # Save the image to a directory
        filename = f"{uuid4().hex}_{post_image.filename}"  # Generating a unique filename
        upload_dir = os.path.join(os.getcwd(), "public", "assets")
        os.makedirs(upload_dir, exist_ok=True)  # Ensuring folder exists
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await post_image.read())  # Saving the file

        image_url = f"/public/assets/{filename}"  # Relative path for frontend/static access

    new_post = BasePost(
        title=title,
        description=description,
        **({"image_url": image_url} if image_url else {}),  # Only include if image_url is not None
        created_by_user_id=created_by_user_id
    )

    return await post_controller.create_post(db, new_post)

@router.get(
    "/details",
    response_model=BaseResponse,
    dependencies=[Depends(verify_token)]
)
async def get_post_details(
    db: AsyncSession = Depends(get_db),
    post_id: int = Query(...),  # Query parameter
):
    """
    Endpoint to fetch details of a specific post.
    - Requires user authentication (validated by the `verify_token` dependency).
    - Accepts the post ID as a query parameter.

    Args:
    - db (AsyncSession): The database session dependency.
    - post_id (int): The ID of the post to fetch.

    Returns:
    - BaseResponse: A response containing the post details or an error message.
    """
    return await post_controller.get_post_details(db, post_id)

@router.patch(
    "/edit",
    response_model=BaseResponse,
    dependencies=[Depends(verify_token)]
)
async def update_post_details(
    title: str = Form(...),
    description: str = Form(...),
    post_id: int = Query(...),  # Query parameter
    user=Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to update details of a specific post.
    - Requires user authentication (validated by the `verify_token` dependency).
    - Accepts post details (title, description) and the post ID.

    Args:
    - title (str): The updated title of the post.
    - description (str): The updated description of the post.
    - post_id (int): The ID of the post to update.
    - user: The authenticated user details.
    - db (AsyncSession): The database session dependency.

    Returns:
    - BaseResponse: A response indicating success or failure.
    """
    logged_in_user_id = user.get('data').get('id')

    updated_post_details = BasePost(
        title=title,
        description=description,
        created_by_user_id=logged_in_user_id
    )

    return await post_controller.update_post(db, post_id, updated_post_details)

@router.delete(
    "/",
    response_model=BaseResponse,
    dependencies=[Depends(verify_token)]
)
async def delete_post_details(
    post_id: int = Query(...),  # Query parameter
    user=Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to delete a specific post.
    - Requires user authentication (validated by the `verify_token` dependency).
    - Accepts the post ID as a query parameter.

    Args:
    - post_id (int): The ID of the post to delete.
    - user: The authenticated user details.
    - db (AsyncSession): The database session dependency.

    Returns:
    - BaseResponse: A response indicating success or failure.
    """
    logged_in_user_id = user.get('data').get('id')
    is_admin = user.get('data').get('is_admin')

    return await post_controller.delete_post(db, post_id, logged_in_user_id, is_admin)

@router.get(
    "/user-posts",
    response_model=BaseResponse,
    dependencies=[Depends(verify_token)]
)
async def get_user_posts(
    user_id: int = Query(...),  # Query parameter
    db: AsyncSession = Depends(get_db),
    user=Depends(verify_token),
):
    """
    Endpoint to fetch all posts created by a specific user. This endpoint will be called from post_service via nginx
    - Requires user authentication (validated by the `verify_token` dependency).
    - Accepts the user ID as a query parameter.

    Args:
    - user_id (int): The ID of the user whose posts are to be fetched.
    - db (AsyncSession): The database session dependency.
    - user: The authenticated user details.

    Returns:
    - BaseResponse: A response containing the user's posts or an error message.
    """
    return await post_controller.get_user_posts(db, user_id)