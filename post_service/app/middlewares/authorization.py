from fastapi import Request, HTTPException, status
import httpx
from core.config import configs
from core.messages import messages

async def verify_token(request: Request):
    """
    Middleware function to verify the authorization token.
    - Extracts the token from the `Authorization` header in the request.
    - Sends the token to the user authentication service for validation via nginx proxy.
    - Raises an HTTPException if the token is invalid or missing.

    Args:
    - request (Request): The incoming HTTP request.

    Returns:
    - dict: The response from the user authentication service if the token is valid.

    Raises:
    - HTTPException: If the token is missing, invalid, or the validation service fails.
    """
    # Extract the token from the Authorization header
    token = request.headers.get("Authorization")
    if not token:
        # Raise an exception if the token is missing
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.TOKEN_REQUIRED
        )

    try:
        # Send the token to the user authentication service for validation
        async with httpx.AsyncClient() as client:
            response = await client.get(
                configs.USER_AUTH_SERVICE_URL + '/validate-token',
                headers={"Authorization": token}
            )

        # Parse the response from the authentication service
        response_data = response.json()

        # Check if the token validation failed
        if response_data and response_data.get("resp_code") != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=response_data.get("message")
            )
        else:
            # Return the user information if the token is valid
            return response.json()
    except Exception as e:
        # Raise an exception if there is an error during token validation
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )