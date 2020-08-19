import math
import datetime
from src.data.collect_bike_data import get_bike_weather_data


def build_train_predict_features(contract, station_number, target):
    data, data_pred = get_bike_weather_data(contract, station_number)
    X, y = prepare_train(data, target)
    X_pred = prepare_pred(data_pred)
    return X, y, X_pred


def prepare_train(data, target):
    y = data[target]
    data.pop(target)
    data['date'] = datetime.datetime.now()
    data['update_date'] = get_date(data['last_update'])
    data['ordinal_date'], data['sin_hour'], data['cos_hour'] = build_time_features(
        data['date'])
    return data, y


def prepare_pred(data_pred):
    data_pred['date'] = datetime.datetime.now()
    data_pred['update_date'] = get_date(
        data_pred['last_update']) + datetime.timedelta(hours=1)
    data_pred['ordinal_date'], data_pred['sin_hour'], data_pred['cos_hour'] = build_time_features(
        data_pred['date'])
    return data_pred


def get_date(ts):
    ts = float(ts)
    try:
        dt = datetime.datetime.fromtimestamp(ts / 1000)
    except (ValueError, TypeError):
        dt = datetime.datetime.now()
    return dt


def build_time_features(date):
    ordinal_date = date.toordinal()
    sin_hour, cos_hour = build_cyclical_hour(date)
    return ordinal_date, sin_hour, cos_hour


def build_cyclical_hour(dt):
    sin_hour = math.sin(2 * math.pi * dt.hour / 24)
    cos_hour = math.cos(2 * math.pi * dt.hour / 24)
    return sin_hour, cos_hour
