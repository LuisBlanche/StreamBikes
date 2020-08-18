import os
import logging
import requests
from flatten_json import flatten

import pandas as pd
from src import settings
from manydataapi.velib import DataCollectJCDecaux


def get_data(contract):
    bikes_api = DataCollectJCDecaux(
        os.environ['API_KEY'], fetch_contracts=True)
    js = bikes_api.get_json(contract)
    df = pd.DataFrame().from_records(js)
    df["last_update"] = pd.to_datetime(df['last_update'])
    df.rename(columns={'lng': 'lon'}, inplace=True)
    return df


def get_station_data(contract, station_number):
    url = f"{settings.STATIONS_API_URL}{station_number}?contract={contract}&apiKey={os.environ['API_KEY']}"
    response = requests.get(url)
    logging.debug(f'Response for url = {url} : {response}')
    return response.json()


def get_latlon_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,daily&appid={os.environ['OPENWEATHER_API_KEY']}"
    response = requests.get(url)
    return response.json()


def get_bike_weather_data(contract, station_number):
    bike_data = get_station_data(contract, station_number)
    lat, lon = bike_data['position']['lat'], bike_data['position']['lng']
    weather = get_latlon_weather(lat, lon)
    bike_data['temp'] = weather["current"]['feels_like']
    bike_data['wind_speed'] = weather["current"]['wind_speed']
    bike_data['clouds'] = weather["current"]['clouds']
    bike_data['main_weather'] = weather["current"]['weather']
    bike_data_pred = bike_data.copy()
    bike_data_pred['temp'] = weather["hourly"][0]['feels_like']
    bike_data_pred['wind'] = weather["hourly"][0]['wind_speed']
    bike_data_pred['clouds'] = weather["hourly"][0]['clouds']
    bike_data_pred['main_weather'] = weather["hourly"][0]['weather']
    bike_data = flatten(bike_data)
    bike_data_pred = flatten(bike_data_pred)
    return bike_data, bike_data_pred
