import requests
from django.conf import settings

class AccuWeatherClient:
    BASE_URL = "http://dataservice.accuweather.com"

    def __init__(self):
        self.api_key = settings.ACCUWEATHER_API_KEY

    def get_current_weather(self, location_key):
        """
        Получить текущую температуру для заданного location_key.
        """
        endpoint = f"{self.BASE_URL}/currentconditions/v1/{location_key}"
        params = {"apikey": self.api_key}
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_historical_weather(self, location_key):
        """
        Получить почасовую температуру за последние 24 часа.
        """
        endpoint = f"{self.BASE_URL}/currentconditions/v1/{location_key}/historical/24"
        params = {"apikey": self.api_key}
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

