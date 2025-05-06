# core/dependencies/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt #dependency for decoding JWT tokens
from core.config import configs
from core.messages import messages
from typing import Optional

# oauth2_scheme is an instance of OAuth2PasswordBearer, which is used to handle token-based authentication.
# - `tokenUrl` specifies the endpoint where clients can obtain a token (in our case, "/auth/sign-in").
# - This is typically used in routes that require authentication, where the token is extracted from the Authorization header.
# - The extracted token is then passed to dependencies for validation and decoding.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/sign-in")

# This function decodes the JWT token and verifies its validity.
# It extracts the user ID from the token payload and checks if it is present.
def decode_token(token: str = Depends(oauth2_scheme)): 
    try:
        if not token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.TOKEN_REQUIRED)
        
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, configs.JWT_SECRET_KEY, algorithms=[configs.ALGORITHM])
        user_id: int = payload.get("id")

        payload["token"] = token  # Add the token to the payload for further use
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_TOKEN)
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
# Method to check if the user is an admin
def check_is_admin(user: dict = Depends(decode_token)):
    if user.get("is_admin") and user.get("is_admin") == 1:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)

# Method to authorize user access based on their role and ID
def authorize_user(
    user_id: Optional[int] = None,
    email: Optional[str] = None,
    logged_in_user: dict = Depends(decode_token),
):
    """
    Authorization logic:
    - Admins can fetch details for any user.
    - Non-admin users can only fetch their own details.
    """

    if logged_in_user.get("is_admin") == 1:
        # Admins are authorized to fetch any user's details
        return

    # Non-admin users can only fetch their own details
    if user_id and user_id != logged_in_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.FORBIDDEN
        )
    if email and email != logged_in_user.get("email"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.FORBIDDEN
        )