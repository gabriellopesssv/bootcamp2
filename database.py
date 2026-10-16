from contextlib import contextmanager
import sqlite3
from pathlib import Path


@contextmanager
def connect(db_path):
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def init_db(db_path):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                region TEXT NOT NULL DEFAULT '',
                country TEXT NOT NULL DEFAULT '',
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
            """
        )


def add_city(city, db_path):
    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO cities (name, region, country, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                city["name"],
                city.get("region", ""),
                city.get("country", ""),
                city["latitude"],
                city["longitude"],
            ),
        )
        return cursor.lastrowid


def list_cities(db_path):
    with connect(db_path) as connection:
        rows = connection.execute(
            "SELECT id, name, region, country, latitude, longitude "
            "FROM cities ORDER BY name COLLATE NOCASE"
        ).fetchall()
        return [dict(row) for row in rows]


def delete_city(city_id, db_path):
    with connect(db_path) as connection:
        cursor = connection.execute("DELETE FROM cities WHERE id = ?", (city_id,))
        return cursor.rowcount > 0
