# Weather API

API для получения данных о погоде, включая текущую погоду, историческую информацию и прогноз.

## Стек технологий

- Django 4.x
- Django REST Framework
- drf-yasg (для документации Swagger)
- AccuWeather API (для получения данных о погоде)

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone <URL вашего репозитория>
   cd <название вашего проекта>
   
2. Создайте виртуальное окружение:
   python3 -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate  # для Windows

3. Установите зависимости:
   pip install -r requirements.txt

4. Создайте файл .env и добавьте ваш API-ключ для AccuWeather:
   ACCUWEATHER_API_KEY=your_api_key_here

5. Выполните миграции:
   python manage.py migrate

6. Запустите сервер:
   python manage.py runserver

7. Документация API доступна по адресу:
   http://127.0.0.1:8000/swagger/

8. Примечания:
Для получения данных о погоде необходимо использовать API-ключ от AccuWeather.
Все запросы к API должны включать параметры location_key или city, 
чтобы определить, для какого города запрашиваются данные.
