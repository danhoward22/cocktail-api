from pydantic import BaseModel

class NewIngredient(BaseModel):
    name: str
    parent_id: int

class Ingredient(BaseModel):
    id: int
    name: str
    parent_id: int