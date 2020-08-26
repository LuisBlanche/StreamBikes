import pytest
from src.data.collect_bike_data import get_station_data, get_latlon_weather, get_bike_weather_data


@pytest.mark.parametrize("contract,station_number", [("lyon", 2010), ("marseille", 1130)])
def test_get_station_data(contract, station_number):
    json = get_station_data(contract, station_number)
    assert isinstance(json, dict)
    assert json['contract_name'] == contract
    assert json['number'] == station_number


@pytest.mark.parametrize("contract,station_number", [("lyon", 0), ("marseill", 1130)])
def test_get_station_data_error(contract, station_number):
    with pytest.raises(ValueError) as ver:
        get_station_data(contract, station_number)
        assert ver == f'This station {station_number} or contract {contract} does not exist'


@pytest.mark.parametrize("contract,station_number", [("lyon", 2010), ("marseille", 1130)])
def test_get_station_data_apikey_error(monkeypatch, contract, station_number):
    monkeypatch.setenv('API_KEY', "invalidapikey")
    with pytest.raises(ConnectionRefusedError) as cer:
        get_station_data(contract, station_number)
        assert cer == "Problem with API key"
