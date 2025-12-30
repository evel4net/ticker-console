import urequests
import utime

from src.config_private import LATITUDE, LONGITUDE, TIMEZONE

class WeatherManager(object):
    def __init__(self):
        self.__weather_api_url = self.__get_weather_api_url()

        self.__temperature = None
        self.__precipitation = None
        self.__weather_code = None
        self.__is_day = None

        self.__last_update_time = None
        self.__delay = 1800 # 30 mins

        self.set_weather()

    def __get_weather_api_url(self) -> str:
        api_url = "https://api.open-meteo.com/v1/forecast"

        parameters = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "temperature_2m,precipitation_probability,weather_code,is_day",
            "timezone": TIMEZONE,
            "forecast_days": 1,
        }

        request_url = api_url + "?"
        for k, v in parameters.items():
            request_url += f"{str(k)}={str(v)}&"

        return request_url[:-1]

    def get_weather(self) -> (float, int, int, bool):
        return self.__temperature, self.__precipitation, self.__weather_code, self.__is_day

    def set_weather(self) -> None:
        response = urequests.get(self.__weather_api_url)
        data = response.json()
        response.close()

        self.__temperature = data['current']['temperature_2m']
        self.__precipitation = data['current']['precipitation_probability']
        self.__weather_code = data['current']['weather_code']
        self.__is_day = data['current']['is_day']

        self.__last_update_time = utime.time()

    def refresh_weather(self) -> bool:
        current_time = utime.time()

        if current_time - self.__last_update_time >= self.__delay:
            self.set_weather()

            return True

        return False