import plotly
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
from datetime import datetime as dt, timedelta as td
import os
import codecs

data_path = '../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'
#time_series_covid19_confirmed_global.csv
#time_series_covid19_deaths_global.csv
#time_series_covid19_recovered_global.csv

pd.read_csv(data_path+'time_series_covid19_confirmed_global.csv')\
    .to_parquet('app/website/static/confirmed.parquet')

pd.read_csv(data_path+'time_series_covid19_deaths_global.csv')\
    .to_parquet('app/website/static/deaths.parquet')

pd.read_csv(data_path+'time_series_covid19_recovered_global.csv')\
    .to_parquet('app/website/static/recovered.parquet')


def world_map():
    df_confirmed = pd.read_parquet('app/website/static/confirmed.parquet')

    df_confirmed.fillna(value='N/A',axis=1, inplace=True)
    df_confirmed['Province/State'] = df_confirmed.apply(
                        lambda row: row['Province/State'] if row['Province/State']!='N/A' else row['Country/Region'],
                        axis=1
                    )

    # use today's value if present, else use last update value
    date = (dt.now() - td(days=1)).strftime('%-m/%-d/%y') if \
                    (dt.now() - td(days=1)).strftime('%-m/%-d/%y') in df_confirmed.columns \
                    else list(df_confirmed.columns)[-1]

    df = df_confirmed[["Country/Region", "Province/State", "Lat", "Long", date]].dropna()

    df.drop(df[df[date]<0].index, inplace=True)

    fig = px.scatter_geo(df, lat="Lat", lon='Long', color="Country/Region",
                         hover_name="Province/State", size=date,
                         projection="natural earth")

    fig_html = fig.to_html(include_plotlyjs='cdn')

    return date, fig_html


if __name__ == '__main__':
    date, fig_html = world_map()
    basedir = os.getcwd()
    with open(basedir+'/app/website/static/world_map.html','w') as htmlfile:
        htmlfile.write(fig_html)

    file = codecs.open(basedir+'/app/website/static/world_map.html', "r", "utf-8")
    print(file.read() == fig_html)
