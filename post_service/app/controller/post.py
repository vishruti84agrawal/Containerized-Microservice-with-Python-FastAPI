from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.post import Post
from schema.post import PostSchema
from core.response import BaseResponse
from core.messages import messages
from schema.post import BasePost
from fastapi import status

class PostService:
    """
    PostService handles all post-related operations, such as creating posts,
    fetching post details, updating posts, and deleting posts.
    """

    @staticmethod
    def serialize_post(post: Post) -> dict:
        """
        Serializes a Post object into a dictionary.
        Args:
        - post (Post): The Post object to serialize.

        Returns:
        - dict: A dictionary representation of the Post object.
        """
        return {
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "image_url": post.image_url,
            "created_by_user_id": post.created_by_user_id,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "is_deleted": post.is_deleted,
        }

    @staticmethod
    async def get_post_title(db: AsyncSession, title: str):
        """
        Fetches a post by its title.
        Args:
        - db (AsyncSession): The database session.
        - title (str): The title of the post.

        Returns:
        - dict: Serialized post details if found, otherwise an empty dictionary.
        """
        try:
            result = await db.execute(select(Post).where(Post.title == title))
            post = result.scalar_one_or_none()
            if post:
                return PostService.serialize_post(post)
            else:
                return {}
        except Exception as e:
            print("get_post_title Error:", e)
            return {}

    async def create_post(self, db: AsyncSession, schema: BasePost):
        """
        Creates a new post in the database.
        Args:
        - db (AsyncSession): The database session.
        - schema (BasePost): The post creation schema.

        Returns:
        - BaseResponse: A response indicating success or failure.
        """
        try:
            # Check if a post with the same title already exists
            result = await db.execute(select(Post).where(Post.title == schema.title))
            new_post = result.scalar_one_or_none()

            if new_post:
                return BaseResponse(
                    resp_code=status.HTTP_409_CONFLICT,
                    message=messages.POST_ALREADY_EXISTS,
                )
            else:
                # Create a new post
                new_post = Post(
                    title=schema.title,
                    description=schema.description,
                    image_url=schema.image_url,
                    created_by_user_id=schema.created_by_user_id,
                )
                db.add(new_post)
                await db.commit()
                await db.refresh(new_post)

                return BaseResponse(
                    resp_code=status.HTTP_201_CREATED,
                    message=messages.POST_CREATION_SUCCESS,
                )
        except Exception as e:
            db.rollback()
            return BaseResponse(
                resp_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e),
            )

    async def get_post_details(self, db: AsyncSession, post_id: int):
        """
        Fetches details of a specific post by its ID.
        Args:
        - db (AsyncSession): The database session.
        - post_id (int): The ID of the post.

        Returns:
        - BaseResponse: A response containing post details or an error message.
        """
        try:
            result = await db.execute(select(Post).where(Post.id == post_id))
            post = result.scalar_one_or_none()
            if post:
                post_details = PostSchema.from_orm(post).dict()  # Convert to dictionary
                return BaseResponse(
                    resp_code=200,
                    message=messages.POST_DETAILS_SUCCESS,
                    data=post_details,
                )
            else:
                return BaseResponse(
                    resp_code=404,
                    message=messages.POST_NOT_FOUND,
                )
        except Exception as e:
            print("get_post_details Error:", e)
            return BaseResponse(
                resp_code=500,
                message=messages.INTERNAL_SERVER_ERROR,
            )

    async def get_post_list(self, db: AsyncSession):
        """
        Fetches a list of all posts that are not deleted.
        Args:
        - db (AsyncSession): The database session.

        Returns:
        - BaseResponse: A response containing the list of posts or an error message.
        """
        try:
            result = await db.execute(select(Post).where(Post.is_deleted == 0))
            posts = result.scalars().all()  # Fetch all posts that are not deleted
            if posts:
                post_list = [PostSchema.from_orm(post).dict() for post in posts]
                return BaseResponse(
                    resp_code=200,
                    message=messages.POST_LIST_SUCCESS,
                    data=post_list,
                )
            else:
                return BaseResponse(
                    resp_code=200,
                    message=messages.NO_RECORDS,
                    data=[],
                )
        except Exception as e:
            print("get_post_list Error:", e)
            return BaseResponse(
                resp_code=500,
                message=messages.INTERNAL_SERVER_ERROR,
            )

    async def update_post(self, db: AsyncSession, post_id: int, post_details: BasePost):
        """
        Updates details of a specific post.
        Args:
        - db (AsyncSession): The database session.
        - post_id (int): The ID of the post to update.
        - post_details (BasePost): The updated post details.

        Returns:
        - BaseResponse: A response indicating success or failure.
        """
        try:
            # Fetch the post to be updated. Only the creator can update it.
            result = await db.execute(
                select(Post).where(
                    (Post.id == post_id)
                    & (Post.created_by_user_id == post_details.created_by_user_id)
                    & (Post.is_deleted == 0)
                )
            )
            post = result.scalar_one_or_none()
            if post:
                stmt = {}

                post_details = dict(post_details)

                if post_details["title"]:
                    stmt["title"] = post_details["title"]
                if post_details["description"]:
                    stmt["description"] = post_details["description"]

                # Update the data
                for key, value in stmt.items():
                    setattr(post, key, value)  # Set the attribute dynamically

                db.add(post)
                await db.commit()
                await db.refresh(post)

                return BaseResponse(
                    resp_code=200,
                    message=messages.POST_UPDATE_SUCCESS,
                )
            else:
                return BaseResponse(
                    resp_code=404,
                    message=messages.POST_NOT_FOUND,
                )
        except Exception as e:
            print("update_post Error:", e)
            return BaseResponse(
                resp_code=500,
                message=messages.INTERNAL_SERVER_ERROR,
            )

    async def delete_post(self, db: AsyncSession, post_id: int, user_id: int, is_admin: int):
        """
        Deletes a specific post (soft delete).
        Args:
        - db (AsyncSession): The database session.
        - post_id (int): The ID of the post to delete.
        - user_id (int): The ID of the user requesting the deletion.
        - is_admin (int): Whether the user is an admin.

        Returns:
        - BaseResponse: A response indicating success or failure.
        """
        try:
            # Check if the user is an admin or the creator of the post
            if is_admin:
                result = await db.execute(
                    select(Post).where((Post.id == post_id) & (Post.is_deleted == 0))
                )
            else:
                result = await db.execute(
                    select(Post).where(
                        (Post.id == post_id)
                        & (Post.created_by_user_id == user_id)
                        & (Post.is_deleted == 0)
                    )
                )

            post = result.scalar_one_or_none()
            if post:
                # Soft delete the post by setting is_deleted to 1
                post.is_deleted = 1
                db.add(post)
                await db.commit()
                await db.refresh(post)

                return BaseResponse(
                    resp_code=200,
                    message=messages.POST_DELETE_SUCCESS,
                )
            else:
                return BaseResponse(
                    resp_code=404,
                    message=messages.POST_NOT_FOUND,
                )
        except Exception as e:
            print("delete_post Error:", e)
            return BaseResponse(
                resp_code=500,
                message=messages.INTERNAL_SERVER_ERROR,
            )

    async def get_user_posts(self, db: AsyncSession, user_id: int):
        """
        Fetches all posts created by a specific user.
        Args:
        - db (AsyncSession): The database session.
        - user_id (int): The ID of the user.

        Returns:
        - BaseResponse: A response containing the user's posts or an error message.
        """
        try:
            result = await db.execute(
                select(Post).where(
                    (Post.created_by_user_id == user_id) & (Post.is_deleted == 0)
                )
            )
            posts = result.scalars().all()
            if posts:
                post_list = [PostSchema.from_orm(post).dict() for post in posts]
                return BaseResponse(
                    resp_code=200,
                    message=messages.POST_LIST_SUCCESS,
                    data=post_list,
                )
            else:
                return BaseResponse(
                    resp_code=200,
                    message=messages.NO_RECORDS,
                    data=[],
                )
        except Exception as e:
            print("get_user_posts Error:", e)
            return BaseResponse(
                resp_code=500,
                message=messages.INTERNAL_SERVER_ERROR,
            )