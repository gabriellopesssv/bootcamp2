import sqlite3
import tempfile
import unittest
from pathlib import Path

import database


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "cities.db"
        database.init_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_city_persists_city_for_listing(self):
        city = {
            "name": "Brasília",
            "region": "Distrito Federal",
            "country": "Brasil",
            "latitude": -15.79,
            "longitude": -47.88,
        }

        city_id = database.add_city(city, self.db_path)

        self.assertGreater(city_id, 0)
        self.assertEqual(database.list_cities(self.db_path), [{**city, "id": city_id}])

    def test_delete_city_removes_it(self):
        city_id = database.add_city(
            {
                "name": "Recife",
                "latitude": -8.05,
                "longitude": -34.9,
            },
            self.db_path,
        )

        self.assertTrue(database.delete_city(city_id, self.db_path))
        self.assertEqual(database.list_cities(self.db_path), [])
        self.assertFalse(database.delete_city(city_id, self.db_path))

    def test_city_names_are_unique_without_case_sensitivity(self):
        city = {"name": "Brasília", "latitude": -15.79, "longitude": -47.88}
        database.add_city(city, self.db_path)

        with self.assertRaises(sqlite3.IntegrityError):
            database.add_city({**city, "name": "brasília"}, self.db_path)


if __name__ == "__main__":
    unittest.main()
