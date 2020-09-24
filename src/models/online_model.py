import datetime
import logging
import numbers
import time

from creme import (compose, feature_extraction, linear_model, metrics, optim,
                   preprocessing, stats, time_series)

from src.features.build_features import build_train_predict_features


def get_hour(x):
    x['hour'] = x['date'].hour
    return x


def define_pipeline(list_cat_features, list_num_features, learning_rate):
    """Creates the modeling pipeline for online learning

    Returns
    -------
    model: creme.compose.Pipeline
        modeling pipeline to fit
    metric: creme.metric.
        a metric to monitor during online learning
    """
    init = optim.initializers.Normal(mu=0, sigma=1, seed=42)
    num = compose.Select(*list_num_features) | preprocessing.StandardScaler()
    cat = compose.SelectType(
        *list_cat_features) | preprocessing.OneHotEncoder()
    mean_target = get_hour | feature_extraction.TargetAgg(
        by=['hour'], how=stats.BayesianMean(
            prior=3,
            prior_weight=1)) | preprocessing.StandardScaler()
    model = compose.Pipeline(
        num + cat + mean_target,
        linear_model.LinearRegression(
            optimizer=optim.SGD(learning_rate), intercept_lr=0.001, initializer=init)
    )

    model = time_series.Detrender(regressor=model, window_size=60)

    metric = metrics.Rolling(metrics.MAE(), 60)
    return model, metric


def online_learn(contract, station, list_cat_features, list_num_features, target, timestep=120, learning_rate=0.1):
    """Launches online regression for target with list of features at a given station (time step every minute)

    Parameters
    ----------
    contract : str
        city we are looking at
    station : int
        station identifier
    list_features : list
        list of features to include into the model
    target : str
        name of the target variable
    """
    model, metric = define_pipeline(
        list_cat_features, list_num_features, learning_rate=learning_rate)
    real_y = {}
    predicted_y = {}
    t = 0
    while True:
        t += 1
        X, y, X_pred = build_train_predict_features(contract, station, target)
        real_y[str(X['date'].hour) + str(X['date'].minute)] = y

        y_pred_one, y_pred_1h, metric, model = train_pred_step(
            X, y, X_pred, model, metric)
        predicted_y[str(X['date'].hour) + str(X['date'].minute)] = y_pred_1h
        logging.info(f'Metric = {metric}, y pred = {y_pred_one}, y true = {y}')

        logging.info(f'Predicted available bikes in 1 hour : {y_pred_1h}')
        if t > 3600 / timestep:
            date_1h = X['date'] - datetime.timedelta(minutes=60)
            try:
                logging.info(
                    f"Real number of bikes 1 hour ago = {real_y[date_1h]}")
            except KeyError:
                logging.error('Pb with the date')
                pass
        time.sleep(timestep)


def train_pred_step(X, y, X_pred, model, metric):
    """[summary]

    Parameters
    ----------
    X : [type]
        [description]
    y : [type]
        [description]
    X_pred : [type]
        [description]
    model : [type]
        [description]
    metric : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    y_pred_one = model.predict_one(X)
    metric = metric.update(y, y_pred_one)
    model = model.fit_one(X, y)
    y_pred_1h = model.predict_one(X_pred)
    return y_pred_one, y_pred_1h, metric, model
