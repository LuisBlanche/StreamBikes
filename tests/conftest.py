import pytest
import requests


@pytest.fixture
def mock_response_weather(monkeypatch):
    """Requests.get() mocked to return
     {'mock_key':'mock_response'}."""
    def mock_post(*args, **kwargs):
        r = requests.Response()
        r.status_code = 200
        r.json = {}
        return r
    monkeypatch.setattr(requests, "get", mock_post)
