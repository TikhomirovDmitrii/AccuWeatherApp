from django.core.cache import cache
from .api_client import AccuWeatherClient
from datetime import datetime
from django.utils.timezone import make_aware
import pytz  # Для работы с временными зонами
from django.conf import settings
import requests
from django.http import JsonResponse
import logging




def health_check(request):
    """
    Эндпоинт проверки состояния сервера.
    """
    return JsonResponse({"status": "OK"})


def current_weather(request):
    # URL и параметры запроса к API
    api_url = f"https://api.accuweather.com/currentconditions/v1/12345"
    params = {"apikey": settings.ACCUWEATHER_API_KEY}

    try:
        response = requests.get("URL_внешнего_API", params={'city': request.GET.get('city')})
        response.raise_for_status()  # Это вызовет ошибку, если код состояния != 2xx
        return JsonResponse(response.json(), status=200)
    except requests.exceptions.RequestException as e:
        # Если ошибка, возвращаем 500
        return JsonResponse({"error": str(e)}, status=500)

def historical_weather(request):
    """
    Эндпоинт для получения почасовой температуры за последние 24 часа.
    """
    location_key = "295212"  # Пример для Москвы
    cache_key = f"historical_weather_{location_key}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return JsonResponse(cached_data, safe=False)

    client = AccuWeatherClient()
    try:
        weather_data = client.get_historical_weather(location_key)
        if weather_data:
            # Преобразуем данные в удобный формат
            processed_data = [
                {
                    "datetime": entry["LocalObservationDateTime"],
                    "temperature": entry["Temperature"]["Metric"]["Value"],
                    "unit": entry["Temperature"]["Metric"]["Unit"],
                    "description": entry["WeatherText"],
                }
                for entry in weather_data
            ]
            # Сохраняем в кэш на 1 час (3600 секунд)
            cache.set(cache_key, processed_data, timeout=3600)
            return JsonResponse(processed_data, safe=False)
        else:
            return JsonResponse({"error": "No data found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def historical_weather_max(request):
    """
    Эндпоинт для получения максимальной температуры за последние 24 часа.
    """
    location_key = "295212"  # Пример для Москвы
    cache_key = f"historical_weather_{location_key}"
    historical_data = cache.get(cache_key)

    if not historical_data:
        return JsonResponse({"error": "Historical data not available"}, status=404)

    max_temp = max(historical_data, key=lambda x: x["temperature"])
    return JsonResponse({
        "datetime": max_temp["datetime"],
        "temperature": max_temp["temperature"],
        "unit": max_temp["unit"],
        "description": max_temp["description"]
    })

def historical_weather_min(request):
    """
    Эндпоинт для получения минимальной температуры за последние 24 часа.
    """
    location_key = "295212"  # Пример для Москвы
    cache_key = f"historical_weather_{location_key}"
    historical_data = cache.get(cache_key)

    if not historical_data:
        return JsonResponse({"error": "Historical data not available"}, status=404)

    min_temp = min(historical_data, key=lambda x: x["temperature"])
    return JsonResponse({
        "datetime": min_temp["datetime"],
        "temperature": min_temp["temperature"],
        "unit": min_temp["unit"],
        "description": min_temp["description"]
    })

def historical_weather_avg(request):
    """
    Эндпоинт для получения средней температуры за последние 24 часа.
    """
    location_key = "295212"  # Пример для Москвы
    cache_key = f"historical_weather_{location_key}"
    historical_data = cache.get(cache_key)

    if not historical_data:
        return JsonResponse({"error": "Historical data not available"}, status=404)

    avg_temp = sum(entry["temperature"] for entry in historical_data) / len(historical_data)
    return JsonResponse({
        "average_temperature": round(avg_temp, 2),
        "unit": historical_data[0]["unit"]
    })

def weather_by_time(request):
    """
    Эндпоинт для поиска температуры, ближайшей к переданному timestamp.
    """
    timestamp = request.GET.get("timestamp")
    if not timestamp:
        return JsonResponse({"error": "Timestamp parameter is required"}, status=400)

    try:
        # Конвертируем timestamp в объект datetime
        requested_time = make_aware(datetime.fromtimestamp(int(timestamp)), pytz.UTC)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid timestamp"}, status=400)

    location_key = "295212"  # Пример для Москвы
    cache_key = f"historical_weather_{location_key}"
    historical_data = cache.get(cache_key)

    if not historical_data:
        return JsonResponse({"error": "Historical data not available"}, status=404)

    # Найдем запись с минимальной разницей времени
    def time_difference(entry):
        entry_time = datetime.fromisoformat(entry["datetime"]).replace(tzinfo=pytz.UTC)
        return abs((entry_time - requested_time).total_seconds())

    closest_entry = min(historical_data, key=time_difference)
    closest_time = datetime.fromisoformat(closest_entry["datetime"]).replace(tzinfo=pytz.UTC)

    # Проверяем, попадает ли ближайшее время в допустимый интервал (например, 1 час)
    if abs((closest_time - requested_time).total_seconds()) > 3600:
        return JsonResponse({"error": "No matching time found within 1 hour"}, status=404)

    return JsonResponse({
        "datetime": closest_entry["datetime"],
        "temperature": closest_entry["temperature"],
        "unit": closest_entry["unit"],
        "description": closest_entry["description"],
    })

logger = logging.getLogger(__name__)


def weather_forecast(request):
    """
    Эндпоинт для получения прогноза погоды на ближайшие 5 дней.
    """
    location_key = "295212"  # locationKey для Санкт-Петербурга
    api_url = f"https://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"

    params = {
        "apikey": settings.ACCUWEATHER_API_KEY,
        "details": "true"  # Для получения подробной информации
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Это вызовет ошибку, если код состояния != 2xx

        # Обработка данных прогноза
        data = response.json()
        forecast = [
            {
                "date": forecast["Date"],
                "temperature_max": forecast["Temperature"]["Maximum"]["Value"],
                "temperature_min": forecast["Temperature"]["Minimum"]["Value"],
                "day": forecast["Day"]["IconPhrase"],
                "night": forecast["Night"]["IconPhrase"]
            }
            for forecast in data["DailyForecasts"]
        ]
        return JsonResponse(forecast, safe=False)

    except requests.exceptions.RequestException as e:
        # Логируем ошибку с деталями
        logger.error(f"Error fetching weather forecast: {str(e)}")
        return JsonResponse({"error": "Failed to retrieve data from the weather API", "details": str(e)}, status=500)


