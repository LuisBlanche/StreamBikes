import pytest
from src.data.collect_bike_data import get_station_data, get_latlon_weather, get_bike_weather_data


@pytest.mark.parametrize("contract,station_number", [("lyon", 2010), ("marseille", 1130)])
def test_get_station_data(contract, station_number):
    json = get_station_data(contract, station_number)
    assert isinstance(json, dict)
    assert json['contract_name'] == contract
    assert json['number'] == station_number


@pytest.mark.parametrize("contract,station_number", [("lyon", 0), ("marseill", 1130)])
def test_get_station_data_value_error(contract, station_number):
    with pytest.raises(ValueError) as ver:
        get_station_data(contract, station_number)
        assert ver == f'This station {station_number} or contract {contract} does not exist'


@pytest.mark.parametrize("contract,station_number", [("lyon", 2010), ("marseille", 1130)])
def test_get_station_data_apikey_error(monkeypatch, contract, station_number):
    monkeypatch.setenv('API_KEY', "invalidapikey")
    with pytest.raises(ConnectionRefusedError) as cre:
        get_station_data(contract, station_number)
        assert cre == "Problem with Bikes API key"


@pytest.mark.parametrize("lat,lon", [(35, 40), (45.6, 3.7)])
def test_get_latlon_weather(lat, lon):
    json = get_latlon_weather(lat, lon)
    assert isinstance(json, dict)
    assert json['lat'] == lat
    assert json['lon'] == lon


@pytest.mark.parametrize("lat,lon", [(350, 4), (4, 4555), ("x", 5), (5, "t")])
def test_get_latlon_weather_value_error(lat, lon):
    with pytest.raises(ValueError) as ver:
        get_latlon_weather(lat, lon)
        assert ver == f"Latitude = {lat}, Longitude = {lon} is an invalid position"


@pytest.mark.parametrize("lat,lon", [(43, 20), (4, 53.6)])
def test_get_latlon_weather_apikey_error(monkeypatch, lat, lon):
    monkeypatch.setenv('OPENWEATHER_API_KEY', "invalidapikey")
    with pytest.raises(ConnectionRefusedError) as cre:
        get_latlon_weather(lat, lon)
        assert cre == "Problem with Weather API key"


@pytest.mark.parametrize("contract,station_number", [("lyon", 2010), ("marseille", 1130)])
def test_get_bike_weather_data(mock_get_station_data, mock_get_latlon_weather, contract, station_number):

    bike_data, bike_data_pred = get_bike_weather_data(contract, station_number)
    assert isinstance(bike_data, dict)
    assert isinstance(bike_data_pred, dict)
    assert set(bike_data.keys()) == set(bike_data_pred.keys())
    assert list(map(type, bike_data.values())) == list(
        map(type, bike_data_pred.values()))
    assert bike_data['number'] == bike_data_pred['number']
    assert bike_data_pred['contract_name'] == bike_data_pred['contract_name']
