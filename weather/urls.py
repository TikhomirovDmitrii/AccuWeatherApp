from django.urls import path
from . import views

app_name = 'weather'  # Здесь устанавливаем пространство имен

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('weather/current/', views.current_weather, name='current_weather'),
    path('weather/historical/', views.historical_weather, name='historical_weather'),
    path('weather/historical/max/', views.historical_weather_max, name='historical_weather_max'),
    path('weather/historical/min/', views.historical_weather_min, name='historical_weather_min'),
    path('weather/historical/avg/', views.historical_weather_avg, name='historical_weather_avg'),
    path('weather/by_time/', views.weather_by_time, name='weather_by_time'),
    path('weather/forecast/', views.weather_forecast, name='weather_forecast'),
    path('forecast/', views.weather_forecast, name='weather_forecast'),
]

