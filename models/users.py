from pydantic import BaseModel

class UserResponse(BaseModel):
    success: bool
    message: str | None = None
    link: str | None = None