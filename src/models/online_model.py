import logging
import time
import datetime
from creme import compose, linear_model, metrics, preprocessing, optim, time_series
from src.features.build_features import build_train_predict_features


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
    categ_processing = compose.Select(
        *list_cat_features) | preprocessing.OneHotEncoder()
    num_processing = compose.Select(
        *list_num_features) | preprocessing.StandardScaler()
    model = compose.Pipeline(
        categ_processing + num_processing,
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
