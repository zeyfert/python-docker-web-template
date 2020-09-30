import requests
from pymongo import MongoClient
from datetime import datetime, time


class OpenWeather(object):
    """OpenWeather API.

    API provides current weather and forecast.
    Official documentation - https://openweathermap.org/api.
    The class prepaires a report based on API's information.
    The report includes statistics from 9 a.m. till 6 p.m.
    Because only this time frame is relevant for windsurfing.

    Parameters:
        type_report (str): you may choose:
            1. 'weather' - to show current (today) weather
            2. 'forecast' - to show forecast for next 4 days
        city (str): the name of a city for watching
        token (str): you can get it on the official site of API

    """
    def __init__(self, city, token):
        self.city = city
        self.token = token
        self.url = self.get_url_open_weather
        self.check_connection


    @property
    def get_url_open_weather(self):
        """Create url for Openweathermap API

        Returns:
            url (str): it will be used as base for methods which are represented below
        """
        return 'https://api.openweathermap.org/data/2.5/' \
               'forecast?q={c}&units=metric&appid={t}' \
               .format( c=self.city, t=self.token)


    @property
    def check_connection(self):
        """Check connection to the API

        In the case of fault, an exception will be raised
        And the script stops.

        Returns:
            string (str): 'Ok' or exception description

        """
        response = requests.get(self.url).status_code
        if response == 200:
            return 'Ok'
        else:
            raise ValueError(
                f'Server response is {response}. ' \
                'Please check your token and spelling of the type_report/city',
            )


    def get_data_list(self):
        """Provides forecast of weather attributes for 4 days 

        Returns:
            forecast (list): list of dictionaries with all attributes
        Example:
            [
                {'dt': 1600117200,
                 'main': {'temp': 26.2, 'feels_like': 27.87, ... },
                  ...
                 'wind': {'speed': 2.93, 'deg': 336}, ... },
                {'dt': 1600128000,
                 'main': {'temp': 24.6, 'feels_like': 26.4, ... },
                 ...
                 'wind': {'speed': 1.89, 'deg': 349}, ... },
                 ...
            ]
        """
        return requests.get(self.url).json()['list']


    def get_relevant_attributes(self, data_list):
        """Provides the forecast.

        All information which is not required is exclude,
        And leaves timestamp, temperature, humidity,
        Speed and angle of wind.

        Return:
            forecast (list): list of dictionaries
            with relevant information (timestamp, wind speed)

        Example:
            [
                {'timestamp': datetime.datetime(2020, 9, 20, 15, 0),
                 'temperature': 29.93,
                 'humidity': 50,
                 'wind_speed': 5.15,
                 'wind_degree': 187}
                 ...
            ]
        """
        def get_attributes_for_one_period(one_period):
            """Exports only timestamp and wind speed parameters from the dictionary
               It will be used in map function
            """
            timestamp = datetime.fromtimestamp(one_period['dt'])
            return {
                'timestamp': timestamp,
                'datetime_str': timestamp.strftime('%d.%m\n%H:%M'),
                'temperature': one_period['main']['temp'],
                'humidity': one_period['main']['humidity'],
                'wind_speed': one_period['wind']['speed'],
                'wind_degree': one_period['wind']['deg'],
            }

        return list(map(get_attributes_for_one_period, data_list))


    def get_daylight_data(self, relevant_attributes_list):
        """Provides the forecast for the daytime (9:00:00 <= x <= 18:00:00)

        Returns:
            forecast (list): only relevant time periods

        Example:
            [
                {'timestamp': datetime.datetime(2020, 9, 15, 9, 0),
                 'wind_speed': 2.93},
                 ...
                {'timestamp': datetime.datetime(2020, 9, 15, 18, 0),
                 'wind_speed': 1.89},
            ]
        """
        def is_correct_time(one_period):
            """Checks if the value between 9:00 and 18:00.

            Parameters:
                 one time frame forecast (dict):

            Returns:
                bool value: True or False

            """
            if time(9) <= one_period['timestamp'].time() <= time(18):
                return True
            return False

        return list(filter(is_correct_time, relevant_attributes_list))


    def get_rounded_values(self, daylight_relevant_attributes):
        """Rounds the values.

        Parameters:
            All relevant time periods with attributes (list): list of dictionaries

        Returns:
            Rounded values

        """
        def round_values(one_period):
            one_period['temperature'] = round(one_period['temperature'], 1)
            one_period['wind_speed'] = round(one_period['wind_speed'], 1)
            return one_period
        return list(map(round_values, daylight_relevant_attributes))


    def prepare_relevant_forecast(self):
        data_list = self.get_data_list()
        relevant_attribites = self.get_relevant_attributes(data_list)
        daylight_relevant_attributes = self.get_daylight_data(relevant_attribites)
        return self.get_rounded_values(daylight_relevant_attributes)


    def send_data_to_mongo(self):
        client = MongoClient()
        client = MongoClient('db_mongo', 27017)
        db = client.flask_db
        collection = db.api_data
        data = self.prepare_relevant_forecast()
        for item in data:
            collection.update_one(
                {"timestamp": item['timestamp']},
                {"$set": {
                    "datetime_str": item['datetime_str'],
                    "temperature": item['temperature'],
                    "humidity": item['humidity'],
                    "wind_speed": item['wind_speed'],
                    "wind_degree": item['wind_degree'],
                }},
                upsert=True,
            )
