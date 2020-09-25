import logging
from typing import Any, Dict, Tuple

import requests
from flatten_json import flatten

from src import settings


def get_station_data(contract: str, station_number: int) -> Dict[str, Any]:
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
    logging.debug(f"Response for url = {url} : {response}")
    if response.status_code == 404:
        raise ValueError(
            f"Station: {station_number} or contrac: {contract} does not exist"
        )
    elif response.status_code == 403:
        raise ConnectionRefusedError("Problem with Bikes API key")
    else:
        return response.json()


def get_latlon_weather(lat: float, lon: float) -> Dict[str, Any]:
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
            f"Latitude = {lat}, Longitude = {lon} is an invalid position"
        )
    elif response.status_code == 401:
        raise ConnectionRefusedError("Problem with Weather API key")
    else:
        return response.json()


def get_bike_weather_data(
    contract: str, station_number: int
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Collect bike and weather data and split between train and pred

    Parameters
    ----------
    contract : str
        city where the station is
    station_number : int
        station identifier

    Returns
    -------
    Tuple[Dict[str, Any], Dict[str, Any]]
        two jsons with the training and prediction data
    """
    bike_data = get_station_data(contract, station_number)
    lat, lon = bike_data["position"]["lat"], bike_data["position"]["lng"]
    weather = get_latlon_weather(lat, lon)
    bike_train_data = join_bike_weather_train_data(bike_data, weather)
    bike_pred_data = join_bike_weather_pred_data(bike_data, weather)

    return bike_train_data, bike_pred_data


def join_bike_weather_train_data(
    bike_data: Dict[str, Any], weather_data: Dict[str, Any]
) -> Dict[str, Any]:
    """joins bike data and weather.

    Parameters
    ----------
    bike_data : Dict[str, Any]
        json with bike station data
    weather_data : Dict[str, Any]
        json with weather data

    Returns
    -------
    Dict[str, Any]
        json with both data
    """
    bike_data["temp"] = weather_data["current"]["feels_like"]
    bike_data["wind_speed"] = weather_data["current"]["wind_speed"]
    bike_data["clouds"] = weather_data["current"]["clouds"]
    bike_data["main_weather"] = weather_data["current"]["weather"]
    bike_data = flatten(bike_data)

    return bike_data


def join_bike_weather_pred_data(
    bike_data: Dict[str, Any], weather_data: Dict[str, Any]
) -> Dict[str, Any]:
    """joins bike data and weather prediction.

    Parameters
    ----------
    bike_data : Dict[str, Any]
        json with bike station data
    weather_data : Dict[str, Any]
        json with weather data

    Returns
    -------
    Dict[str, Any]
        json with both data
    """
    bike_data["temp"] = weather_data["hourly"][0]["feels_like"]
    bike_data["wind_speed"] = weather_data["hourly"][0]["wind_speed"]
    bike_data["clouds"] = weather_data["hourly"][0]["clouds"]
    bike_data["main_weather"] = weather_data["hourly"][0]["weather"]
    bike_data = flatten(bike_data)
    return bike_data
