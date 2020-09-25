import datetime

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

from src.application.data_for_dash import (
    filter_df,
    get_data,
    get_df_from_redis,
    get_prediction_error,
    get_weather_pred_from_redis,
)
from src.settings import conf

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    external_stylesheets=[dbc.themes.SOLAR],
)

server = app.server


app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                html.H2(
                    f"""Bike Stream for station
                        n°{conf.station} in {conf.contract}"""
                )
            ],
            justify="center",
            align="center",
        ),
        dbc.Row(html.H3(id="score"), justify="center", align="center"),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="bikes-forecast",
                        figure=go.Figure(
                            layout=dict(
                                font={"color": "#082255"}, height=500,
                            )
                        ),
                    )
                ),
                dbc.Col(dt.DataTable(id="weather")),
            ],
            justify="center",
            align="center",
        ),
        dt.DataTable(id="table"),
        dbc.Row(),
        dcc.Interval(id="update", interval=conf.interval, n_intervals=0,),
    ]
)


@app.callback(
    [
        Output("weather", "data"),
        Output("weather", "columns"),
        Output("bikes-forecast", "figure"),
        Output("table", "data"),
        Output("table", "columns"),
        Output("score", "children"),
    ],
    [Input("update", "n_intervals")],
    [State("bikes-forecast", "figure")],
)
def gen_forecast_graph(data, figure):
    """

    :params interval: update the graph based on an interval
    """
    weights = get_data(
        conf.contract, conf.station, [], conf.features, "available_bikes"
    )
    columns = [
        {"name": i, "id": i, "type": "numeric", "format": {"specifier": ".3"}}
        for i in weights.keys()
    ]
    data = get_df_from_redis(
        [
            "date",
            "available_bikes",
            "available_bikes_1min",
            "available_bikes_1h",
        ]
    )

    weather, weather_columns = get_weather_pred_from_redis()
    print(weather)
    print(weights)

    data = filter_df(data)
    data = data.drop_duplicates(subset=["date"])
    mae = get_prediction_error(data)
    trace = [
        dict(
            type="scatter",
            x=data["date"],
            y=data["available_bikes"],
            line={"color": "blue"},
            hoverinfo=data["available_bikes"],
            mode="lines+markers",
            name="Available Bikes",
        ),
        dict(
            type="scatter",
            x=data["date"] + datetime.timedelta(hours=1),
            # add max(predicted, max_station)
            y=round(data["available_bikes_1h"]),
            line={"color": "red"},
            hoverinfo=data["available_bikes"],
            mode="lines+markers",
            name="Predicted Available Bikes",
        ),
    ]

    figure["data"] = trace
    return (
        weather,
        weather_columns,
        figure,
        [weights],
        columns,
        f"MAE score over last hour = {mae}",
    )


if __name__ == "__main__":
    app.run_server(debug=True)
