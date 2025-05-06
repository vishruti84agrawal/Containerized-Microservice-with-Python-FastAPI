from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from core.config import configs

class JWTManager:
    """Service for handling JWT operations."""

    def __init__(self):
        self.secret_key = configs.JWT_SECRET_KEY
        self.algorithm = configs.ALGORITHM
        self.expiration_minutes = int(configs.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Create a new JWT token with the given data and expiration time.
    # The token will include the expiration time as a claim.
    def create_access_token(self, data: Dict[str, str], expires_delta: Optional[timedelta] = None) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.expiration_minutes)
        
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt