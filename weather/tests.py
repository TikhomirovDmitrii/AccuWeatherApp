import requests
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from unittest.mock import MagicMock


class WeatherAPITestCase(TestCase):
    @patch('weather.views.requests.get')  # Мокаем requests.get внутри weather.views
    def test_current_weather(self, mock_get):
        # Настройка мока для симуляции успешного ответа API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "Temperature": {"Metric": {"Value": 15, "Unit": "C"}}
        }

        # Запрос к эндпоинту current_weather
        response = self.client.get(reverse('weather:current'))

        # Проверяем, что статус ответа 200
        self.assertEqual(response.status_code, 200)

        # Проверяем, что в ответе есть ключ "Temperature"
        self.assertIn("Temperature", response.json())

    @patch('weather.views.requests.get')  # Мокаем requests.get внутри weather.views
    def test_api_error_handling(self, mock_get):
        # Настройка мока для симуляции ошибки API
        mock_get.side_effect = requests.exceptions.RequestException("API error")

        # Запрос к эндпоинту current_weather
        response = self.client.get(reverse('weather:current'))

        # Проверяем, что статус ответа 500 (ошибка внешнего API)
        self.assertEqual(response.status_code, 500)

        # Проверяем, что в ответе есть сообщение об ошибке
        self.assertIn("error", response.json())

    @patch('weather.views.AccuWeatherClient')  # Мокаем класс AccuWeatherClient
    def test_historical_weather_success(self, MockClient):
        """
        Проверка успешного получения исторических данных о погоде.
        """
        # Создаем объект клиента и настраиваем его
        mock_client = MagicMock()
        MockClient.return_value = mock_client

        # Мокаем успешный ответ от метода get_historical_weather
        mock_client.get_historical_weather.return_value = [
            {
                "LocalObservationDateTime": "2024-12-12T12:00:00",
                "Temperature": {"Metric": {"Value": 5, "Unit": "C"}},
                "WeatherText": "Clear sky"
            },
            {
                "LocalObservationDateTime": "2024-12-12T13:00:00",
                "Temperature": {"Metric": {"Value": 7, "Unit": "C"}},
                "WeatherText": "Partly cloudy"
            }
        ]

        # Запрос к эндпоинту historical_weather
        response = self.client.get(reverse('weather:historical'))

        # Проверяем, что статус ответа 200
        self.assertEqual(response.status_code, 200)

        # Проверяем, что ответ содержит два элемента данных
        self.assertEqual(len(response.json()), 2)

        # Проверяем, что данные правильные
        self.assertEqual(response.json()[0]['temperature'], 5)
        self.assertEqual(response.json()[1]['temperature'], 7)

    @patch('weather.views.AccuWeatherClient')  # Мокаем класс AccuWeatherClient
    def test_historical_weather_no_data(self, MockClient):
        """
        Проверка обработки ошибки, когда исторические данные не найдены.
        """
        # Создаем объект клиента и настраиваем его
        mock_client = MagicMock()
        MockClient.return_value = mock_client

        # Мокаем ответ от метода get_historical_weather с пустыми данными
        mock_client.get_historical_weather.return_value = None

        # Запрос к эндпоинту historical_weather
        response = self.client.get(reverse('weather:historical'))

        # Проверяем, что статус ответа 404 (данные не найдены)
        self.assertEqual(response.status_code, 404)

        # Проверяем, что в ответе есть сообщение об ошибке
        self.assertIn("error", response.json())
        self.assertEqual(response.json()["error"], "No data found")

    @patch('weather.views.cache.get')  # Мокаем cache.get для симуляции получения данных
    def test_historical_weather_min_success(self, mock_cache_get):
        # Данные, которые вернет мокаемая функция cache.get
        mock_cache_get.return_value = [
            {"datetime": "2024-12-12T10:00:00", "temperature": 5, "unit": "C", "description": "Clear"},
            {"datetime": "2024-12-12T11:00:00", "temperature": 8, "unit": "C", "description": "Partly Cloudy"},
            {"datetime": "2024-12-12T12:00:00", "temperature": 3, "unit": "C", "description": "Cloudy"}
        ]

        # Запрос к эндпоинту для получения минимальной температуры
        response = self.client.get(reverse('weather:historical_min'))

        # Проверяем, что статус ответа 200
        self.assertEqual(response.status_code, 200)

        # Проверяем, что в ответе есть информация о минимальной температуре
        self.assertIn("temperature", response.json())
        self.assertEqual(response.json()["temperature"], 3)
        self.assertEqual(response.json()["unit"], "C")
        self.assertEqual(response.json()["description"], "Cloudy")

    @patch('weather.views.cache.get')  # Мокаем cache.get для симуляции получения данных
    def test_historical_weather_min_no_data(self, mock_cache_get):
        # Мокаем ситуацию, когда данные отсутствуют в кеше
        mock_cache_get.return_value = None

        # Запрос к эндпоинту для получения минимальной температуры
        response = self.client.get(reverse('weather:historical_min'))

        # Проверяем, что статус ответа 404
        self.assertEqual(response.status_code, 404)

        # Проверяем, что в ответе есть сообщение об ошибке
        self.assertIn("error", response.json())
        self.assertEqual(response.json()["error"], "Historical data not available")