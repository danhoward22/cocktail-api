from pydantic import BaseModel

class CocktailIngredient(BaseModel):
    id: int
    name: str | None = None
    parents: list[str] = []
    qty: float
    units: str

class Garnish(BaseModel):
    id: int
    name: str | None = None
    qty: float

class PayloadCocktail(BaseModel):
    id: int | None = None
    name: str
    source: str = ""
    notes: str = ""
    ingredients: list[CocktailIngredient]
    garnishes: list[Garnish] = []

class Cocktail(PayloadCocktail):
    id: int
