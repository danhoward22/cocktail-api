from typing import Literal
from pydantic import BaseModel, Field

class CocktailIngredient(BaseModel):
    id: int = Field(..., gt=0)
    name: str | None = None
    parents: list[str] = []
    qty: float = Field(..., gt=0)
    units: Literal["cup","oz","tbsp","tsp","mL","dash","drops",""]

class Garnish(BaseModel):
    id: int = Field(..., gt=0)
    name: str | None = None
    qty: float = Field(..., gt=0)

class PayloadCocktail(BaseModel):
    id: int | None = Field(default=None, gt=0)
    name: str = Field(..., min_length=1)
    source: str = ""
    notes: str = ""
    ingredients: list[CocktailIngredient] = Field(..., min_length=1)
    garnishes: list[Garnish] = []

class Cocktail(PayloadCocktail):
    id: int = Field(..., gt=0)
