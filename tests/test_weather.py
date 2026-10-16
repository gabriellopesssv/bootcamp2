import unittest
from unittest.mock import patch

import weather


class WeatherTests(unittest.TestCase):
    @patch("weather.fetch_json")
    def test_search_city_returns_normalized_location(self, fetch_json):
        fetch_json.return_value = {
            "results": [
                {
                    "name": "Brasília",
                    "admin1": "Distrito Federal",
                    "country": "Brasil",
                    "latitude": -15.79,
                    "longitude": -47.88,
                }
            ]
        }

        city = weather.search_city(" Brasília ")

        self.assertEqual(city["name"], "Brasília")
        self.assertEqual(city["region"], "Distrito Federal")
        self.assertEqual(city["country"], "Brasil")
        self.assertEqual(city["latitude"], -15.79)

    @patch("weather.fetch_json", return_value={"results": []})
    def test_search_city_reports_unknown_location(self, _fetch_json):
        with self.assertRaisesRegex(weather.WeatherServiceError, "Nenhuma cidade"):
            weather.search_city("Cidade inexistente")

    def test_describes_weather_codes_and_unknown_values(self):
        self.assertEqual(weather.describe_weather_code(0), "Céu limpo")
        self.assertEqual(
            weather.describe_weather_code(999), "Condição não informada"
        )

    @patch(
        "weather.fetch_json",
        return_value={
            "current": {
                "temperature_2m": 24.5,
                "relative_humidity_2m": 61,
                "weather_code": 2,
            }
        },
    )
    def test_get_current_weather_normalizes_api_data(self, _fetch_json):
        self.assertEqual(
            weather.get_current_weather(-15.79, -47.88),
            {
                "temperature": 24.5,
                "humidity": 61,
                "description": "Parcialmente nublado",
            },
        )


if __name__ == "__main__":
    unittest.main()
