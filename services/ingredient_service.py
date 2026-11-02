from sqlite3 import Connection, IntegrityError
from models.ingredients import Ingredient, PayloadIngredient

def get_parent_ingredient_names(db: Connection, parent_id: int | None) -> list[str]:
    if not parent_id:
        return []

    cursor = db.cursor()
    cursor.execute(
        """
        WITH RECURSIVE ingredient_tree AS (
            SELECT `id`, `name`, `parent_id`
            FROM ingredients
            WHERE `id` = :parent_id

            UNION ALL

            SELECT 
                parent.id, 
                parent.name, 
                parent.parent_id
            FROM ingredients parent
            INNER JOIN ingredient_tree child ON parent.id = child.parent_id
        )

        SELECT `name` FROM ingredient_tree
        """,
        {"parent_id":parent_id}
    )

    parent_names = [row[0] for row in cursor.fetchall()]
    return parent_names

def query_ingredients_list(db: Connection, /, *,
    sort_by: str = "name"
) -> list[Ingredient]:
    
    cursor = db.cursor()

    query = "SELECT * FROM ingredients"
    if sort_by == "id": query += " ORDER BY `id` ASC"
    if sort_by == "name": query += " ORDER BY `name` ASC"
    cursor.execute(query)

    ingredients_list = [
        Ingredient(id=i["id"], name=i["name"], parent_id=i["parent_id"])
        for i in cursor.fetchall()
    ]

    return ingredients_list

def query_ingredient(db: Connection, ingredient_id: int) -> Ingredient | None:
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM ingredients WHERE `id` = :id",
        {"id":ingredient_id}
    )
    i = cursor.fetchone()

    return None if not i else Ingredient(id=i["id"], name=i["name"], parent_id=i["parent_id"])

def insert_ingredient(db: Connection, ingredient: PayloadIngredient) -> Ingredient | str:
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO ingredients
            (`name`, `parent_id`)
            VALUES (:name, :parent_id)
            """,
            {"name": ingredient.name, "parent_id": ingredient.parent_id}
        )
        ingredient_id = cursor.lastrowid
        db.commit()

        return query_ingredient(db, ingredient_id)
    except IntegrityError as e:
        print(e)
        return str(e)

def upsert_ingredient(db: Connection, ingredient: Ingredient) -> Ingredient | str:
    cursor = db.cursor()
    try:
        #Check for circular reference
        cursor.execute(
            """
            WITH RECURSIVE ParentTree AS (
                SELECT id, parent_id
                FROM ingredients
                WHERE id = :proposed_parent_id
                
                UNION ALL
                
                SELECT i.id, i.parent_id
                FROM ingredients i
                JOIN ParentTree pt ON i.id = pt.parent_id
            )
            SELECT 1 
            FROM ParentTree 
            WHERE id = :current_ingredient_id;
            """,
            {"proposed_parent_id":ingredient.parent_id, "current_ingredient_id":ingredient.id}
        )

        if cursor.fetchone():
            return "Parent ID is a circular reference"

        cursor.execute(
            """
            UPDATE ingredients
            SET `name`=:name, `parent_id`=:parent_id
            WHERE `id`=:id
            """,
            {"name": ingredient.name, "parent_id": ingredient.parent_id, "id":ingredient.id}
        )

        if not cursor.rowcount:
            return "Ingredient ID does not exist"

        db.commit()
    except IntegrityError as e:
        print(e)
        return str(e)

    return query_ingredient(db, ingredient.id)

def delete_ingredient_record(db: Connection, ingredient_id: int) -> bool | str:

    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM ingredients WHERE `id` = :id",
            {"id": ingredient_id}
        )
        if not cursor.rowcount: return False
    except IntegrityError as e:
        print(e)
        return str(e)

    db.commit()

    return True