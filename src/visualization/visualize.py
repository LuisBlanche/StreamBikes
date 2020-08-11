import os
import time
import json
import pydeck as pdk
import numpy as np
import pandas as pd
import streamlit as st
from src import settings
from manydataapi.velib import DataCollectJCDecaux

contract = "lyon"
st.write(f'## {contract} bikeshare stations data')
last_rows = np.random.randn(1, 1)

st.cache()


def get_data(contract):
    bikes_api = DataCollectJCDecaux(
        os.environ['API_KEY'], fetch_contracts=True)
    js = bikes_api.get_json(contract)
    df = pd.DataFrame().from_records(js)
    df["last_update"] = pd.to_datetime(df['last_update'])
    df.rename(columns={'lng': 'lon'}, inplace=True)
    return df


n_bikes = st.sidebar.number_input(
    'Minimum Available Bikes', step=1, value=0, min_value=0, max_value=200)
df = get_data(contract)
data = df.loc[df['available_bikes'] > n_bikes,
              ['lat', 'lon', 'available_bikes', 'last_update']]
f"### Last updated station = {df['last_update'].min()}"
midpoint = (np.average(data['lat']), np.average(data['lon']))
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=midpoint[0],
        longitude=midpoint[1],
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=data,
            get_position='[lon, lat]',
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        )
    ],
))

data
