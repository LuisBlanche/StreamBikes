import dash
import os
import logging
import pandas as pd
import redis
import datetime
from sklearn.metrics import mean_absolute_error
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

from src.models.online_model import train_pred_step, define_pipeline
from src.features.build_features import build_train_predict_features

contract = 'lyon'
station = '2010'
features = ['logtemp', 'logwind', 'clouds', 'sin_hour',
            'cos_hour', 'logtempXsinhour', 'logtempXcoshour', 'weekday']


def get_data(contract, station, list_cat_features, list_num_features, target, learning_rate=0.1):
    X, y, X_pred = build_train_predict_features(contract, station, target)
    model, metric = define_pipeline(
        list_cat_features, list_num_features, learning_rate=learning_rate)
    y_pred_one, y_pred_1h, metric, model = train_pred_step(
        X, y, X_pred, model, metric)
    logging.info("X:", [(k, X[k])
                        for k in features])
    logging.info("Pred", [(k, X_pred[k])
                          for k in features])
    data = {}
    data["date"] = str(X['date'])
    data["available_bikes"] = int(y)
    data["available_bikes_1min"] = float(y_pred_one)
    data["available_bikes_1h"] = float(y_pred_1h)
    logging.info(dict(model.regressor["LinearRegression"].weights))
    push_to_redis(data)
    return dict(model.regressor["LinearRegression"].weights)


def push_to_redis(data):
    r = redis.Redis(host="localhost")
    for k, v in data.items():
        r.rpush(k, v)


def get_df_from_redis(keys):
    r = redis.Redis(host="localhost")
    df = pd.DataFrame()
    for k in keys:
        df[k] = r.lrange(k, 0, -1)
    df['date'] = pd.to_datetime(df['date'].str.decode('utf-8'))
    df['available_bikes'] = df['available_bikes'].astype(int)
    df['available_bikes_1min'] = df['available_bikes_1min'].astype(float)
    df['available_bikes_1h'] = df['available_bikes_1h'].astype(float)
    return df


def get_prediction_error(data):
    if len(data) > 60:
        data = data.set_index('date')
        data['available_bikes_1h'] = data['available_bikes_1h'].shift(60)
        data_last_hour = data.iloc[-60:]
        mae = mean_absolute_error(
            data_last_hour['available_bikes'], data_last_hour['available_bikes_1h'])
    else:
        mae = 'Wait for one hour to get MAE'
    return mae


GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 6000)

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],


)

server = app.server


app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div([html.H2("Bike Stream"),
                       html.H3(id='score'),
                       dcc.Graph(id='bikes-forecast', figure=dict(layout=dict(
                           plot_bgcolor=app_color["graph_bg"],
                           paper_bgcolor=app_color["graph_bg"]),
                       )),
                       dash_table.DataTable(id='table'),

                       dcc.Interval(
    id="update",
    interval=60000,
    n_intervals=0,
), ])


@ app.callback(
    [Output("bikes-forecast", "figure"), Output("table", "data"), Output("table", "columns"), Output("score", "children")
     ], [Input("update", "n_intervals")]
)
def gen_forecast_graph(data):
    """

    :params interval: update the graph based on an interval
    """
    weights = get_data(contract, station, [],
                       features, 'available_bikes')
    columns = [{"name": i, "id": i} for i in weights.keys()]
    data = get_df_from_redis(
        ['date', 'available_bikes', 'available_bikes_1min', 'available_bikes_1h'])
    data = data.drop_duplicates(subset=['date'])
    mae = get_prediction_error(data)
    trace = [dict(
        type="scatter",
        x=data['date'],
        y=data["available_bikes"],
        line={"color": "blue"},
        hoverinfo=data["available_bikes"],
        mode="lines+markers",
        name='Available Bikes'
    ), dict(type="scatter",
            x=data['date'] + datetime.timedelta(hours=1),
            y=data["available_bikes_1h"],
            line={"color": "red"},
            hoverinfo=data["available_bikes"],
            mode="lines+markers",
            name="Predicted Available Bikes"
            )]

    layout = dict(
        font={"color": "#fff"},
        height=700,
    )

    return dict(data=trace, layout=layout), [weights], columns, f"MAE score over last hour = {mae}"


if __name__ == '__main__':
    app.run_server(debug=True)
