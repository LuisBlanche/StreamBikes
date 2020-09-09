import os
import logging
import requests
from flatten_json import flatten
import pandas as pd
from src import settings


def get_station_data(contract, station_number):
    """Retrieves last available station data

    Parameters
    ----------
    contract : str
        city where the station is
    station_number : int
        station identifier

    Returns
    -------
    json
        json containing the station level data
    """
    url = f"{settings.STATIONS_API_URL}{station_number}?contract={contract}&apiKey={settings.API_KEYS['DECAUX_API']}"
    response = requests.get(url)
    logging.debug(f'Response for url = {url} : {response}')
    if response.status_code == 404:
        raise ValueError(
            f'Station: {station_number} or contrac: {contract} does not exist')
    elif response.status_code == 403:
        raise ConnectionRefusedError("Problem with Bikes API key")
    else:
        return response.json()


def get_latlon_weather(lat, lon):
    """Returns current OpenWeather API weather and hourly predictions for a given postition

    Parameters
    ----------
    lat : float
        latitude
    lon : float
        longitude

    Returns
    -------
    json
        current weather and hourly predictions
    """

    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,daily&appid={settings.API_KEYS['WEATHER_API']}"
    response = requests.get(url)
    if response.status_code == 400:
        raise ValueError(
            f"Latitude = {lat}, Longitude = {lon} is an invalid position")
    elif response.status_code == 401:
        raise ConnectionRefusedError("Problem with Weather API key")
    else:
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
    bike_data_pred['wind_speed'] = weather["hourly"][0]['wind_speed']
    bike_data_pred['clouds'] = weather["hourly"][0]['clouds']
    bike_data_pred['main_weather'] = weather["hourly"][0]['weather']
    bike_data = flatten(bike_data)
    bike_data_pred = flatten(bike_data_pred)
    return bike_data, bike_data_pred
