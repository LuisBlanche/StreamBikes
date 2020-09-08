import pytest
import requests


def subs_get_latlon_weather(*args, **kwargs):
    return {'lat': 45,
            'lon': 5,
            'timezone': 'Europe/Paris',
            'timezone_offset': 7200,
            'current': {'dt': 1598530275,
                        'sunrise': 1598504194,
                        'sunset': 1598552805,
                        'temp': 302.38,
                        'feels_like': 300.83,
                        'pressure': 1015,
                        'humidity': 32,
                        'dew_point': 284,
                        'uvi': 6.58,
                        'clouds': 7,
                        'visibility': 10000,
                        'wind_speed': 2.6,
                        'wind_deg': 0,
                        'weather': [{'id': 800,
                                     'main': 'Clear',
                                     'description': 'clear sky',
                                     'icon': '01d'}]},
            'hourly': [{'dt': 1598529600,
                        'temp': 302.38,
                        'feels_like': 300.05,
                        'pressure': 1015,
                        'humidity': 32,
                        'dew_point': 284,
                        'clouds': 7,
                        'visibility': 10000,
                        'wind_speed': 3.72,
                        'wind_deg': 10,
                        'weather': [{'id': 800,
                                     'main': 'Clear',
                                     'description': 'clear sky',
                                     'icon': '01d'}],
                        'pop': 0}]}


def subs_get_station_data(*args, **kwargs):
    return {'number': 2010,
            'contract_name': 'lyon',
            'name': '2010 - CONFLUENCE / DARSE',
            'address': 'ANGLE ALLEE ANDRE MURE ET QUAI ANTOINE RIBOUD',
            'position': {'lat': 45.743317, 'lng': 4.815747},
            'banking': True,
            'bonus': False,
            'bike_stands': 22,
            'available_bike_stands': 5,
            'available_bikes': 17,
            'status': 'OPEN',
            'last_update': 1598531569000}


@pytest.fixture()
def mock_get_station_data(monkeypatch):
    from src.data import collect_data
    monkeypatch.setattr(collect_data,
                        'get_station_data', subs_get_station_data)


@pytest.fixture()
def mock_get_latlon_weather(monkeypatch):
    from src.data import collect_data
    monkeypatch.setattr(collect_data,
                        'get_latlon_weather', subs_get_latlon_weather)
