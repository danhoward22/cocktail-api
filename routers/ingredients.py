from fastapi import APIRouter, Depends, Query, Path, status, Response
from sqlite3 import Connection
# from supertokens_python.recipe.session.framework.fastapi import verify_session

from models.ingredients import Ingredient, PayloadIngredient
from database import get_dev_db
from routers.errors import APIError
from services.ingredient_service import query_ingredient, query_ingredients_list, insert_ingredient, upsert_ingredient, delete_ingredient_record
# router = APIRouter(prefix="/api/ingredients", tags=["Ingredients"], dependencies=[Depends(verify_session)])
router = APIRouter(prefix="/api/ingredients", tags=["Ingredients"])

# Object structure returned in API
# const ingredients = [
#   {"id":18, "name":"Lost Spirits Jamaica Rum", "parent_id":17, "user_id":null}
# ]

@router.get("", response_model=list[Ingredient])
def get_ingredients(
    sort_by: str = Query("name", description="Field to sort by (name)"),
    db: Connection = Depends(get_dev_db)
):
    return query_ingredients_list(db, sort_by=sort_by)

@router.get("/{id}", response_model=Ingredient)
def get_ingredient(
    id: int = Path(..., gt=0, description="The ID of the ingredient to get"),
    db: Connection = Depends(get_dev_db)
):
    ingredient = query_ingredient(db, id)

    if not ingredient:
        error_handler("Ingredient ID")
    
    return ingredient

@router.post("", response_model=Ingredient)
def create_ingredient(
    ingredient: PayloadIngredient,
    db: Connection = Depends(get_dev_db)
):
    result = insert_ingredient(db, ingredient)
    
    if isinstance(result, str):
        error_handler(result)

    return result

@router.put("/{id}", response_model=Ingredient)
def update_ingredient(
    ingredient: PayloadIngredient,
    id: int = Path(..., gt=0, description="The ID of the ingredient to update"),
    db: Connection = Depends(get_dev_db)
):
    if ingredient.id and ingredient.id != id:
        error_handler("id mismatch")
    
    params = {"id":id, **ingredient.model_dump(exclude={"id"})}
    ingredient = Ingredient(**params)
    result = upsert_ingredient(db, ingredient)

    if isinstance(result, str):
        error_handler(result)
    
    return result

@router.delete("/{id}")
def delete_ingredient(
    id: int = Path(..., gt=0, description="The ID of the ingredient to delete"),
    db: Connection = Depends(get_dev_db)
):
    result = delete_ingredient_record(db, id)
    
    if isinstance(result, str):
        error_handler(result)

    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        error_handler("Ingredient ID")
    

def error_handler(error: str):
    if "id mismatch" in error:
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="The ID in the body does not match the ID in the URL path."
        )
    if "Ingredient ID" in error:
        raise APIError(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Ingredient ID does not exist.",
            fields={"id": "Ingredient ID does not exist."}
        )
    if "UNIQUE" in error:
        raise APIError(
            status_code=status.HTTP_409_CONFLICT,
            message="Ingredient name already exists.",
            fields={"name": "Ingredient name already exists."}
        )
    if "FOREIGN KEY" in error and "parent_id" in error:
        raise APIError(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message="Parent ingredient does not exist.",
            fields={"parent_id": "Parent ingredient does not exist."}
        )
    if "circular" in error:
        raise APIError(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message="Parent ID is a circular reference.",
            fields={"parent_id": "Parent ID is a circular reference."}
        )
    raise APIError(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Could not save ingredient."
    )