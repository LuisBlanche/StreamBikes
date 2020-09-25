import datetime
import logging

import pandas as pd
import redis
from sklearn.metrics import mean_absolute_error

from src import settings
from src.features.build_features import build_train_predict_features
from src.models.online_model import define_pipeline, train_pred_step
from src.settings import conf


def get_data(
    contract,
    station,
    list_cat_features,
    list_num_features,
    target,
    learning_rate=0.1,
):
    X, y, X_pred = build_train_predict_features(contract, station, target)
    model, metric = define_pipeline(
        list_cat_features, list_num_features, learning_rate=learning_rate
    )
    y_pred_one, y_pred_1h, metric, model = train_pred_step(
        X, y, X_pred, model, metric
    )
    logging.debug(f"X:{[(k, X[k]) for k in conf.features]}")
    logging.debug(f"Pred: {[(k, X_pred[k]) for k in conf.features]}")
    data = {}
    data["date"] = str(X["date"])
    data["available_bikes"] = int(y)
    data["available_bikes_1min"] = float(y_pred_one)
    data["available_bikes_1h"] = float(y_pred_1h)
    data["predicted_temp"] = X_pred["temp"]
    data["predicted_wind"] = X_pred["wind_speed"]
    data["predicted_clouds"] = X_pred["clouds"]
    logging.info(dict(model.regressor["LinearRegression"].weights))
    push_to_redis(data)
    return dict(model.regressor["LinearRegression"].weights)


def push_to_redis(data):
    r = redis.Redis(host=settings.REDIS)
    for k, v in data.items():
        r.rpush(k, v)


def get_df_from_redis(keys):
    r = redis.Redis(host=settings.REDIS)
    df = pd.DataFrame()
    for k in keys:
        df[k] = r.lrange(k, 0, -1)
    df["date"] = pd.to_datetime(df["date"].str.decode("utf-8"))
    df["available_bikes"] = df["available_bikes"].astype(int)
    df["available_bikes_1min"] = df["available_bikes_1min"].astype(float)
    df["available_bikes_1h"] = df["available_bikes_1h"].astype(float)
    return df


def get_weather_pred_from_redis():
    r = redis.Redis(host=settings.REDIS)
    df = pd.DataFrame()
    for k in ["predicted_temp", "predicted_wind", "predicted_clouds"]:
        df[k] = r.lrange(k, -1, -1)
        df[k] = df[k].astype(float)
    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict("records")
    return data, columns


def filter_df(df, timespan=24):
    now = datetime.datetime.now()
    delta = datetime.timedelta(hours=timespan)
    df = df[now - df["date"] < delta]
    return df


def get_prediction_error(data):
    if len(data) > 3600 / (conf.interval / 1000):
        data = data.set_index("date")
        data["available_bikes_1h"] = data["available_bikes_1h"].shift(30)
        data_last_hour = filter_df(data, 1)
        mae = mean_absolute_error(
            data_last_hour["available_bikes"],
            data_last_hour["available_bikes_1h"],
        )
    else:
        mae = "Wait for one hour to get MAE"
    return mae
