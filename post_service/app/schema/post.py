from pydantic import BaseModel, Field
from typing import Optional, Any

class BasePost(BaseModel):
    """
    BasePost schema to define common fields for post-related operations.
    - `title`: The title of the post (required, 3-100 characters).
    - `description`: The description of the post (required, 3-1000 characters).
    - `image_url`: Optional field to store the URL or path of an image associated with the post.
    - `created_by_user_id`: Optional field to store the ID of the user who created the post.
    """
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=3, max_length=1000)
    image_url: Optional[str] = None  # Optional image file upload
    created_by_user_id: Optional[int] = Field(None, description="User ID of the creator")

class PostSchema(BasePost):
    """
    PostSchema extends BasePost and includes additional fields for database operations.
    - `id`: The unique identifier for the post (optional).
    - `image_url`: Field to store the image URL or path (optional, overrides BasePost).
    - `created_at`: Timestamp indicating when the post was created (optional).
    - `updated_at`: Timestamp indicating when the post was last updated (optional).
    - `is_deleted`: Indicates whether the post is deleted (optional, 0 or 1).
    - `is_active`: Indicates whether the post is active (optional, 0 or 1).

    Config:
    - `orm_mode`: Enables compatibility with ORM objects (e.g., SQLAlchemy models).
    - `from_attributes`: Allows Pydantic to map attributes from ORM objects (Pydantic v2.0+ feature).
    """
    id: Optional[int] = Field(None, description="Post ID")
    image_url: Optional[str] = None  # Field to store the image URL or path
    created_at: Optional[Any] = Field(None, description="Creation timestamp")
    updated_at: Optional[Any] = Field(None, description="Last update timestamp")
    is_deleted: Optional[int] = Field(None, description="Is the post deleted?")
    is_active: Optional[int] = Field(None, description="Is the post active?")

    class Config:
        orm_mode = True  # Enables ORM compatibility
        from_attributes = True  # Allows mapping attributes from ORM objects