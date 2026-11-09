from fastapi import APIRouter, Depends, Query, Path, status, Response
from sqlite3 import Connection
# from supertokens_python.recipe.session.framework.fastapi import verify_session

from models.cocktails import Cocktail, PayloadCocktail, CocktailPage
from database import get_dev_db
from routers.errors import APIError
from services.cocktail_service import query_cocktail, query_cocktails_list, insert_cocktail, upsert_cocktail, delete_cocktail_record
# router = APIRouter(prefix="/api/cocktails", tags=["Cocktails"], dependencies=[Depends(verify_session)])
router = APIRouter(prefix="/api/cocktails", tags=["Cocktails"])

# Object structure returned in API
# const cocktails = [
#   {
#     id:5, name:"Mai Tai",
#     ingredients:[
#       {id:18, name:"Lost Spirits Jamaica Rum", parents:["Jamaican Rum","Rum"], qty:2, units:"oz"},
#       {id:20, name:"Orange Curaçao", parents:["Curaçao"], qty:.5, units:"oz"},
#       {id:19, name:"Lime Juice", parents:[], qty:1, units:"oz"},
#       {id:21, name:"Orgeat", parents:[], qty:.5, units:"oz"},
#     ],
#     garnishes:[
#       {id:22, name:"Mint Sprig", qty:1},
#       {id:23, name:"Lime Shell", qty:1},
#     ],
#     notes:"Shake, serve on rocks. Arrange mint and spent lime shell like an island with a palm tree.",
#     source:"",
#   },
# ]

@router.get("", response_model=CocktailPage)
def get_cocktails(
    response: Response,
    sort: str = Query("id", description="Field to sort by (id or name)"),
    limit: int = Query(500, gt=0, le=500, description="Cocktail count limit per page"),
    offset: int = Query(0, ge=0, description="Page offset to return"),
    db: Connection = Depends(get_dev_db)
):
    response.headers["Cache-Control"] = "public, max-age=300"
    cocktails, total = query_cocktails_list(db, sort_by=sort, limit=limit, offset=offset)

    result = CocktailPage(total=total, limit=limit, offset=offset, cocktails=cocktails)
    if isinstance(result, str):
        error_handler(result)

    return result

@router.get("/{id}", response_model=Cocktail)
def get_cocktail(
    response: Response,
    id: int = Path(..., gt=0, description="The ID of the cocktail to get"),
    db: Connection = Depends(get_dev_db)
):
    response.headers["Cache-Control"] = "public, max-age=300"
    cocktail = query_cocktail(db, id)
    if not cocktail:
        error_handler("Cocktail ID")

    return cocktail

@router.post("", response_model=Cocktail)
def create_cocktail(
    cocktail: PayloadCocktail,
    db: Connection = Depends(get_dev_db)
):
    result = insert_cocktail(db, cocktail)
    
    if isinstance(result, str):
        error_handler(result)

    return result

@router.put("/{id}", response_model=Cocktail)
def update_cocktail(
    cocktail: PayloadCocktail,
    id: int = Path(..., gt=0, description="The ID of the cocktail to update"),
    db: Connection = Depends(get_dev_db)
):
    if cocktail.id and cocktail.id != id:
        error_handler("id mismatch")

    params = {"id":id, **cocktail.model_dump(exclude={"id"})}
    cocktail = Cocktail(**params)
    result = upsert_cocktail(db, cocktail)

    if isinstance(result, str):
        error_handler(result)
    
    return result

@router.delete("/{id}")
def delete_cocktail(
    id: int = Path(..., gt=0, description="The ID of the cocktail to delete"),
    db: Connection = Depends(get_dev_db)
):
    result = delete_cocktail_record(db, id)
    
    if isinstance(result, str):
        error_handler(result)
    
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        error_handler("Cocktail ID")

def error_handler(error: str):
    if "id mismatch" in error:
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="The ID in the body does not match the ID in the URL path."
        )
    if "Cocktail ID" in error:
        raise APIError(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Cocktail ID does not exist.",
            fields={"id": "Cocktail ID does not exist."}
        )
    if "UNIQUE" in error:
        raise APIError(
            status_code=status.HTTP_409_CONFLICT,
            message="Cocktail name and source already exists.",
            fields={"name": "Cocktail name and source already exists."}
        )
    if "FOREIGN KEY" in error and "ingredient" in error:
        raise APIError(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message="Selected ingredient does not exist.",
            fields={"ingredients": "Selected ingredient does not exist."}
        )
    if "FOREIGN KEY" in error and "garnish" in error:
        raise APIError(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message="Selected garnish does not exist.",
            fields={"garnishes": "Selected garnish does not exist."}
        )
    if "Duplicate" in error:
        message="Duplicate ingredients in cocktail."
        fields={}
        if "ingredient" in error:
            fields["ingredients"] = "Duplicate ingredients in cocktail."
        else:
            message="Duplicate garnishes in cocktail."

        if "garnish" in error:
            fields["garnishes"] = "Duplicate garnishes in cocktail."

        raise APIError(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message=message,
            fields=fields
        )

    raise APIError(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Could not save cocktail."
    )