from os import environb
import pytest
import os


def test_get_redis_dev():
    from src.settings import get_redis_host
    assert get_redis_host('dev') == 'localhost'


def test_get_redis_docker():
    from src.settings import get_redis_host
    assert get_redis_host('docker') == 'redis_service'


def test_get_redis_fail():
    with pytest.raises(ValueError) as ver:
        from src.settings import get_redis_host
        get_redis_host('wrong_env')
    assert 'ENV variable may either be "travis", "dev" or "docker" in .env' in str(
        ver.value)


def test_get_api_keys_fail_name(caplog):
    from src.settings import get_api_keys
    assert get_api_keys('wrong_name', 'dev') is None
    assert "Did not find" in caplog.text


def test_get_api_keys_fail_env():
    from src.settings import get_api_keys
    with pytest.raises(ValueError) as ver:
        get_api_keys("api_keys", "wrong_env")
    assert 'ENV variable may either be "travis", "dev" or "docker" in .env' in str(
        ver.value)


def test_get_api_keys():
    from src.settings import get_api_keys
    keys = get_api_keys('api_keys', 'dev')
    assert keys is not None
    assert set(keys) == set(['DECAUX_API', 'WEATHER_API'])
