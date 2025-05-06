from sqlalchemy import Column, Integer, String
from models.base import BaseModelSettings

class Post(BaseModelSettings):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String,unique=True, nullable=False)
    description = Column(String, nullable=True)

    # Image field
    # Want to store the image URL or path in the database
    image_url = Column(String, nullable=True, default=None)  # or image_path

    # This is just a normal field storing external user ID
    created_by_user_id = Column(Integer, nullable=False) #reference who created the post
