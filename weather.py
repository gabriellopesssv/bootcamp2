import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class WeatherServiceError(Exception):
    pass


WEATHER_CODES = {
    0: "Céu limpo",
    1: "Predominantemente limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Neblina",
    48: "Neblina congelante",
    51: "Garoa leve",
    53: "Garoa moderada",
    55: "Garoa intensa",
    61: "Chuva leve",
    63: "Chuva moderada",
    65: "Chuva intensa",
    71: "Neve leve",
    73: "Neve moderada",
    75: "Neve intensa",
    80: "Pancadas de chuva leves",
    81: "Pancadas de chuva moderadas",
    82: "Pancadas de chuva fortes",
    95: "Trovoada",
    96: "Trovoada com granizo leve",
    99: "Trovoada com granizo forte",
}


def fetch_json(url):
    request = Request(url, headers={"User-Agent": "ClimaEmFoco/1.0"})
    try:
        with urlopen(request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise WeatherServiceError(
            "Não foi possível consultar o serviço de clima. Tente novamente."
        ) from error


def search_city(name):
    query = name.strip()
    if not 2 <= len(query) <= 80:
        raise ValueError("Informe uma cidade com 2 a 80 caracteres.")

    params = urlencode(
        {"name": query, "count": 1, "language": "pt", "format": "json"}
    )
    data = fetch_json(f"https://geocoding-api.open-meteo.com/v1/search?{params}")
    results = data.get("results") or []
    if not results:
        raise WeatherServiceError("Nenhuma cidade encontrada com esse nome.")

    result = results[0]
    return {
        "name": result["name"],
        "region": result.get("admin1", ""),
        "country": result.get("country", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"],
    }


def describe_weather_code(code):
    return WEATHER_CODES.get(code, "Condição não informada")


def get_current_weather(latitude, longitude):
    params = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code",
            "timezone": "auto",
        }
    )
    data = fetch_json(f"https://api.open-meteo.com/v1/forecast?{params}")
    current = data.get("current")
    if not current:
        raise WeatherServiceError("O serviço não retornou as condições atuais.")

    return {
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "description": describe_weather_code(current["weather_code"]),
    }
