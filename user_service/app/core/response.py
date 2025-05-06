from pydantic import BaseModel
from typing import Any, Optional

class BaseResponse(BaseModel):
    """
    BaseResponse is a standardized response model for the API.
    - `resp_code`: HTTP status code or custom response code.
    - `message`: A descriptive message about the response.
    - `data`: Optional field to include additional data (can be a dictionary or a list).
    """
    resp_code: int
    message: str
    data: Optional[dict | list] = None