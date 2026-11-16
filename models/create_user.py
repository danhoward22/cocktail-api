from pydantic import BaseModel

class CreateUserResponse(BaseModel):
    success: bool
    link: str | None = None