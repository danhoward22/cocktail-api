from pydantic import BaseModel

class CocktailIngredient(BaseModel):
    id: int
    name: str
    parents: list[str] = []
    qty: float
    units: str

class Garnish(BaseModel):
    id: int
    name: str
    qty: float

class NewCocktail(BaseModel):
    name: str
    source: str | None = ""
    notes: str | None = ""
    ingredients: list[CocktailIngredient]
    garnishes: list[Garnish] = []

class Cocktail(BaseModel):
    id: int
    name: str
    source: str | None = ""
    notes: str | None = ""
    ingredients: list[CocktailIngredient]
    garnishes: list[Garnish] = []