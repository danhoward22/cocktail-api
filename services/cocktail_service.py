from sqlite3 import Connection, Row
from models.cocktails import *
from services.ingredient_service import get_parent_ingredient_names, get_ingredient

def query_cocktails_list(
    db: Connection,
    sort_by: str = "name"
) -> list[Cocktail]:
    
    cursor = db.cursor()

    cocktail_list = []

    query = "SELECT * FROM drinks"
    if sort_by == "name": query += " ORDER BY `name` ASC"
    cursor.execute(query)

    for drink in cursor.fetchall():
        cocktail_list.append(build_cocktail(drink, db))

    return cocktail_list

def query_cocktail(
    cocktail_id: int,
    db: Connection
) -> Cocktail | None:

    cursor = db.cursor()
    cursor.execute("SELECT * from drinks WHERE `id` = :cocktail_id", {"cocktail_id":cocktail_id})
    drink=cursor.fetchone()

    return None if not drink else build_cocktail(drink, db)

def build_cocktail(
    drink: Row,
    db: Connection
) -> Cocktail:

    parts = []
    garnishes = []
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM drink_ingredients WHERE `drink_id` = :drink_id",
        {"drink_id": drink["id"]}
        )

    for i in cursor.fetchall():
        ingredient = get_ingredient(i["ingredient_id"], db)
        item = {
            "id": i["ingredient_id"],
            "name":ingredient["name"],
            "qty":i["qty"]
            }
        
        if i["is_garnish"]:
            garnishes.append(Garnish(**item))
        else:
            item["units"] = i["units"]
            item["parents"] = get_parent_ingredient_names(ingredient["parent_id"], db)
            parts.append(CocktailIngredient(**item))

    return Cocktail(
        id=drink["id"],
        name=drink["name"],
        source=drink["source"],
        notes=drink["notes"],
        ingredients=parts,
        garnishes=garnishes
    )

# upsert example for future drink_ingredients changes (best for MySQL 8+)
# -- Step 1: Create a temporary table matching your schema
# CREATE TEMPORARY TABLE temp_sync_table LIKE main_table;

# -- Step 2: Bulk insert your HTTP list here using your backend framework
# INSERT INTO temp_sync_table (id, name, value) VALUES (?, ?, ?), (?, ?, ?)...;

# -- Step 3: Delete rows from main table that aren't in the incoming payload
# DELETE FROM main_table 
# WHERE id NOT IN (SELECT id FROM temp_sync_table);

# -- Step 4: Insert new rows and update changed rows efficiently
# INSERT INTO main_table (id, name, value)
# SELECT id, name, value FROM temp_sync_table    
# ON DUPLICATE KEY UPDATE 
#     name = VALUES(name),
#     value = VALUES(value);

# -- Step 5: Clean up
# DROP TEMPORARY TABLE temp_sync_table;


