from pydantic import BaseModel, Field

class PayloadIngredient(BaseModel):
    id: int | None = Field(default=None, gt=0)
    name: str = Field(..., min_length=1)
    parent_id: int | None = Field(default=None, gt=0)

class Ingredient(PayloadIngredient):
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1)
    parent_id: int | None = Field(default=None, gt=0)