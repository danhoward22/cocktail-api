from sqlite3 import Connection

from models.ingredients import Ingredient

def get_ingredient(db: Connection, ingredient_id: int) -> Ingredient | None:
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM ingredients WHERE `id` = :id",
        {"id":ingredient_id}
    )
    return cursor.fetchone()

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
