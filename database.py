import json
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# CREATE_USERS_QUERY = """
#         CREATE TABLE users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username VARCHAR(128) UNIQUE NOT NULL,
#             disabled BOOLEAN DEFAULT FALSE,
#             supertokens_user_id VARCHAR(128) UNIQUE NOT NULL
#         )
#     """

# CREATE_DRINKS_QUERY = """
#         CREATE TABLE drinks (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name VARCHAR(128) NOT NULL,
#             source VARCHAR(128) NOT NULL DEFAULT '',
#             notes VARCHAR(500) NOT NULL DEFAULT '',
#             user_id INTEGER DEFAULT NULL,
#             FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
#             CONSTRAINT unique_drink UNIQUE (name, source, user_id)
#         )
#     """

# CREATE_INGREDIENTS_QUERY = """
#         CREATE TABLE ingredients (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name VARCHAR(128) UNIQUE NOT NULL,
#             parent_id INTEGER DEFAULT NULL,
#             user_id INTEGER DEFAULT NULL,
#             FOREIGN KEY (parent_id) REFERENCES ingredients(id) ON DELETE SET NULL,
#             FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
#         )
#     """

CREATE_DRINKS_QUERY = """
        CREATE TABLE IF NOT EXISTS drinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(128) NOT NULL,
            source VARCHAR(128) NOT NULL DEFAULT '',
            notes VARCHAR(500) NOT NULL DEFAULT '',
            CONSTRAINT unique_drink UNIQUE (name, source)
        )
    """

CREATE_INGREDIENTS_QUERY = """
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(128) UNIQUE NOT NULL,
            parent_id INTEGER DEFAULT NULL,
            FOREIGN KEY (parent_id) REFERENCES ingredients(id) ON DELETE SET NULL
        )
    """

CREATE_DRINK_INGREDIENTS_QUERY = """
        CREATE TABLE IF NOT EXISTS drink_ingredients (
            drink_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            qty FLOAT NOT NULL DEFAULT 0,
            units VARCHAR(15) NOT NULL DEFAULT '',
            is_garnish BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (drink_id) REFERENCES drinks(id) ON DELETE CASCADE,
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
            CONSTRAINT u_drink_ingredient UNIQUE (drink_id, ingredient_id)
        )
    """

_db_conn: sqlite3.Connection | None = None

def load_data(filename: str) -> list:
    file_path = DATA_DIR / filename
    if not file_path.exists():
        return []
    with open(file_path, "r") as f:
        return json.load(f)
        
def init_dev_db():
    global _db_conn
    conn = sqlite3.connect(":memory:", uri=True, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;") 
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    cursor.execute(CREATE_DRINKS_QUERY)
    cursor.execute(CREATE_INGREDIENTS_QUERY)
    cursor.execute(CREATE_DRINK_INGREDIENTS_QUERY)
    
    drink_data = load_data("drinks.json")
    cursor.executemany(
        "INSERT INTO drinks (id, name, source, notes) VALUES (:id, :name, :source, :notes)",
        drink_data
    )

    ingredient_data = load_data("ingredients.json")
    cursor.executemany(
        "INSERT INTO ingredients (id, name, parent_id) VALUES (:id, :name, :parent_id)",
        ingredient_data
    )

    drink_ingredient_data = load_data("drink_ingredients.json")
    cursor.executemany(
        "INSERT INTO drink_ingredients (drink_id, ingredient_id, qty, units, is_garnish) VALUES (:drink_id, :ingredient_id, :qty, :units, :is_garnish)",
        drink_ingredient_data
    )

    conn.commit()

    _db_conn = conn
    
def get_dev_db():
    yield _db_conn

def close_dev_db():
    if _db_conn: _db_conn.close()
