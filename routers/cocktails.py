from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlite3 import Connection
# from supertokens_python.recipe.session.framework.fastapi import verify_session

from models.cocktails import Cocktail, NewCocktail
from database import get_dev_db
from services.cocktail_service import query_cocktails_list, query_cocktail
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

@router.get("", response_model=list[Cocktail])
def get_cocktails(
    sort_by: str = Query("name", description="Field to sort by (name)"),
    db: Connection = Depends(get_dev_db)
):
    return query_cocktails_list(
        db=db,
        sort_by=sort_by
    )

@router.get("/{id}", response_model=Cocktail)
def get_cocktail(
    id: int,
    db: Connection = Depends(get_dev_db)
):
    cocktail = query_cocktail(id, db)
    if not cocktail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cocktail ID does not exist."
        )
    return cocktail

@router.post("")
def create_cocktail(payload: NewCocktail):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="POST not implemented yet. Please try again later."
    )

@router.put("/{id}")
def update_cocktail(id: int, payload: Cocktail):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="PUT not implemented yet. Please try again later."
    )

@router.delete("/{id}")
def delete_cocktail(id: int):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="DELETE not implemented yet. Please try again later."
    )
