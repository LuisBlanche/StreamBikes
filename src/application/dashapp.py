import dash
import os
import datetime
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

from src.settings import conf
from src.application.data_for_dash import get_data, get_df_from_redis, get_prediction_error, filter_df

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
                       html.Div(dash_table.DataTable(id='table'), style={
                                'width': '60%', 'display': 'inline-block', 'vertical-align': 'middle', 'horizontal-align': "middle"}),

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
    weights = get_data(conf.contract, conf.station, [],
                       conf.features, 'available_bikes')
    columns = [{"name": i, "id": i, 'type': 'numeric', 'format': {'specifier': ".3"}}
               for i in weights.keys()]
    data = get_df_from_redis(
        ['date', 'available_bikes', 'available_bikes_1min', 'available_bikes_1h'])
    data = filter_df(data)
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
