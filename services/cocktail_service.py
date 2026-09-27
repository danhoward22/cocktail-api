from sqlite3 import Connection, Row
from models.cocktails import *
from services.ingredient_service import get_parent_ingredient_names, get_ingredient

def query_cocktails_list(db: Connection, /, *,
    sort_by: str = "name"
) -> list[Cocktail]:
    
    cursor = db.cursor()

    query = "SELECT * FROM drinks"
    if sort_by == "name": query += " ORDER BY `name` ASC"
    cursor.execute(query)

    cocktail_list = [
        build_cocktail(db, drink)
        for drink in cursor.fetchall()
    ]

    return cocktail_list

def query_cocktail(db: Connection, cocktail_id: int) -> Cocktail | None:

    cursor = db.cursor()
    cursor.execute(
        "SELECT * from drinks WHERE `id` = :cocktail_id",
        {"cocktail_id":cocktail_id}
    )
    drink=cursor.fetchone()

    return None if not drink else build_cocktail(db, drink)

def build_cocktail(db: Connection, drink: Row) -> Cocktail:

    parts = []
    garnishes = []
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM drink_ingredients WHERE `drink_id` = :drink_id",
        {"drink_id": drink["id"]}
    )

    for i in cursor.fetchall():
        ingredient = get_ingredient(db, i["ingredient_id"])
        item = {
            "id": i["ingredient_id"],
            "name":ingredient["name"],
            "qty":i["qty"]
        }
        
        if i["is_garnish"]:
            garnishes.append(Garnish(**item))
        else:
            item["units"] = i["units"]
            item["parents"] = get_parent_ingredient_names(db, ingredient["parent_id"])
            parts.append(CocktailIngredient(**item))

    return Cocktail(
        id=drink["id"],
        name=drink["name"],
        source=drink["source"],
        notes=drink["notes"],
        ingredients=parts,
        garnishes=garnishes
    )

def insert_cocktail(db: Connection, cocktail: PayloadCocktail) -> Cocktail:
    
    cursor = db.cursor()
    result = cursor.execute(
        """
        INSERT INTO drinks
        (`name`, `source`, `notes`)
        VALUES (:name, :source, :notes)
        """,
        {"name": cocktail.name, "source": cocktail.source, "notes": cocktail.notes}
    )

    cocktail_id = result.lastrowid

    di_rows = [
        {
            "drink_id": cocktail_id,
            "ingredient_id": i.id,
            "qty": i.qty,
            "units": i.units
        }
        for i in cocktail.ingredients
    ]

    cursor.executemany(
        """
        INSERT INTO drink_ingredients
        (`drink_id`, `ingredient_id`, `qty`, `units`)
        VALUES (:drink_id, :ingredient_id, :qty, :units)
        """,
        di_rows
    )

    dg_rows = [
        {
            "drink_id": cocktail_id,
            "ingredient_id": g.id,
            "qty": g.qty,
            "is_garnish": True
        }
        for g in cocktail.garnishes
    ]

    if dg_rows:
        cursor.executemany(
            """
            INSERT INTO drink_ingredients
            (`drink_id`, `ingredient_id`, `qty`, `is_garnish`)
            VALUES (:drink_id, :ingredient_id, :qty, :is_garnish)
            """,
            dg_rows
        )

    db.commit()

    return query_cocktail(db, cocktail_id)

def upsert_cocktail(db: Connection, cocktail: Cocktail) -> Cocktail:
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE drinks
        SET `name`=:name, `source`=:source, `notes`=:notes
        WHERE `id`=:id
        """,
        {"name": cocktail.name, "source": cocktail.source, "notes": cocktail.notes, "id":cocktail.id}
    )

    di_rows = [
        {
            "drink_id": cocktail.id,
            "ingredient_id": i.id,
            "qty": i.qty,
            "units": i.units,
            "is_garnish": False
        }
        for i in cocktail.ingredients
    ]

    for g in cocktail.garnishes:
        di_rows.append({
            "drink_id": cocktail.id,
            "ingredient_id": g.id,
            "qty": g.qty,
            "units": "",
            "is_garnish": True
        })

    cursor.executemany(
        """
        INSERT INTO drink_ingredients
        (`drink_id`, `ingredient_id`, `qty`, `units`, `is_garnish`)
        VALUES (:drink_id, :ingredient_id, :qty, :units, :is_garnish)
        ON CONFLICT (drink_id, ingredient_id, is_garnish)
        DO UPDATE SET qty=:qty, units=:units
        """,
        di_rows
    )

    tuple_placeholders = ", ".join(["(?, ?, ?)"] * len(di_rows))
    
    # We must explicitly match the 3-column structure in the WHERE clause
    delete_query = f"""
        DELETE FROM drink_ingredients
        WHERE (drink_id, ingredient_id, is_garnish)
        NOT IN ({tuple_placeholders});
    """

    delete_params = [
        val 
        for row in di_rows 
        for val in (row["drink_id"], row["ingredient_id"], row["is_garnish"])
    ]

    # Execute the query
    cursor.execute(delete_query, delete_params)
    db.commit()

    return query_cocktail(db, cocktail.id)
