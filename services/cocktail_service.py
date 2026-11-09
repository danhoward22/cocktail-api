from sqlite3 import Connection, Row, IntegrityError
from models.cocktails import *
from services.ingredient_service import get_parent_ingredient_names, query_ingredient

def check_for_duplicate_ingredients(cocktail: PayloadCocktail | Cocktail) -> str:
    errors = ""

    # Check for duplicate ingredients
    i_id = []
    i_dupe = []
    for i in cocktail.ingredients:
        if i.id in i_id and i.id not in i_dupe:
            i_dupe.append(i.id)
        else:
            i_id.append(i.id)

    if i_dupe:
        errors+="Duplicate ingredients. "

    g_id = []
    g_dupe = []
    for g in cocktail.garnishes:
        if g.id in g_id and g.id not in g_dupe:
            g_dupe.append(g.id)
        else:
            g_id.append(g.id)

    if g_dupe:
        errors+="Duplicate garnishes."

    return errors

def query_cocktails_list(db: Connection, /, *,
    sort_by: str = "name",
    limit: int = 500,
    offset: int = 0
) -> tuple[list[Cocktail], int] | str:
    
    cursor = db.cursor()

    try:
        tquery = "SELECT COUNT(*) FROM drinks"
        if sort_by == "id": tquery += " ORDER BY `id` ASC"
        elif sort_by == "name": tquery += " ORDER BY `name` ASC"
        
        cursor.execute(tquery)
        total=cursor.fetchone()[0]

        if total <= limit * offset:
            return [], total

        query = "SELECT * FROM drinks"
        if sort_by == "id": query += " ORDER BY `id` ASC"
        elif sort_by == "name": query += " ORDER BY `name` ASC"
        query += " LIMIT :limit OFFSET :offset"

        cursor.execute("" + query,{"limit": limit, "offset": offset})

        cocktail_list = [
            build_cocktail(db, drink)
            for drink in cursor.fetchall()
        ]

        return cocktail_list, total
    except IntegrityError as e:
        print(e)
        return str(e)


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
        ingredient = query_ingredient(db, i["ingredient_id"])
        item = {
            "id": i["ingredient_id"],
            "name":ingredient.name,
            "qty":i["qty"]
        }
        
        if i["is_garnish"]:
            garnishes.append(Garnish(**item))
        else:
            item["units"] = i["units"]
            item["parents"] = get_parent_ingredient_names(db, ingredient.parent_id)
            parts.append(CocktailIngredient(**item))

    return Cocktail(
        id=drink["id"],
        name=drink["name"],
        source=drink["source"],
        notes=drink["notes"],
        ingredients=parts,
        garnishes=garnishes
    )

def insert_cocktail(db: Connection, cocktail: PayloadCocktail) -> Cocktail | str:
    dupes = check_for_duplicate_ingredients(cocktail)
    if dupes:
        return dupes

    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO drinks
            (`name`, `source`, `notes`)
            VALUES (:name, :source, :notes)
            """,
            {"name": cocktail.name, "source": cocktail.source, "notes": cocktail.notes}
        )
    except IntegrityError as e:
        print(e)
        return str(e)

    try:
        cocktail_id = cursor.lastrowid

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
    except IntegrityError as e:
        print(e)
        return str(e) + " ingredient"
    
    try:
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
    except IntegrityError as e:
        print(e)
        return str(e) + " garnish"

    db.commit()
    return query_cocktail(db, cocktail_id)

def upsert_cocktail(db: Connection, cocktail: Cocktail) -> Cocktail | str:
    dupes = check_for_duplicate_ingredients(cocktail)
    if dupes:
        return dupes
    
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            UPDATE drinks
            SET `name`=:name, `source`=:source, `notes`=:notes
            WHERE `id`=:id
            """,
            {"name": cocktail.name, "source": cocktail.source, "notes": cocktail.notes, "id":cocktail.id}
        )

        if not cursor.rowcount:
            return "Cocktail ID does not exist"
    except IntegrityError as e:
        print(e)
        return str(e)

    try:
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
    except IntegrityError as e:
        print(e)
        return str(e)
    
    try:
        tuple_placeholders = ", ".join(["(?, ?, ?)"] * len(di_rows))
        
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

        cursor.execute(delete_query, delete_params)
    except IntegrityError as e:
        print(e)
        return str(e)

    db.commit()
    return query_cocktail(db, cocktail.id)

def delete_cocktail_record(db: Connection, cocktail_id: int) -> bool | str:

    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM drinks WHERE `id` = :id",
            {"id": cocktail_id}
        )
        if not cursor.rowcount: return False
    except IntegrityError as e:
        print(e)
        return str(e)

    db.commit()

    return True