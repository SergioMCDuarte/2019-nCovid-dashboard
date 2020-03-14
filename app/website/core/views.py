from flask import render_template, request, Blueprint, redirect, url_for
import plotly
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
from datetime import datetime as dt, timedelta as td
import os
#print(os.getcwd())
data_path = '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'

def world_map():
    df_confirmed = pd\
                .read_csv(data_path+'time_series_19-covid-Confirmed.csv')

    df_confirmed.fillna(value='N/A',axis=1, inplace=True)
    df_confirmed['Province/State'] = df_confirmed.apply(
                        lambda row: row['Province/State'] if row['Province/State']!='N/A' else row['Country/Region'],
                        axis=1
                    )

    date = (dt.now() - td(days=1)).strftime('%-m/%-d/%y')

    fig = px.scatter_geo(df_confirmed, lat="Lat", lon='Long', color="Country/Region",
                         hover_name="Province/State", size=date,
                         projection="natural earth",
                         size_max=50)

    fig_html = fig.to_html(include_plotlyjs='cdn')

    return date, fig_html

core = Blueprint('core', __name__)

@core.route('/')
def index():

    if 'fig_html' not in locals() or date != (dt.now() - td(days=1)).strftime('%-m/%-d/%y'):
        date,fig_html = world_map()

    countries_df = pd.read_csv('../countries.csv')
    countries = countries_df.columns.tolist()

    date = (dt.now() - td(days=1)).strftime('%-m/%-d/%y')

    df_confirmed = pd.read_csv(data_path+'time_series_19-covid-Confirmed.csv',
        usecols=['Country/Region', date]).groupby('Country/Region').sum()

    df_deaths = pd.read_csv(data_path+'time_series_19-covid-Deaths.csv',
        usecols=['Country/Region', date]).groupby('Country/Region').sum()

    df_recovered = pd.read_csv(data_path+'time_series_19-covid-Recovered.csv',
        usecols=['Country/Region', date]).groupby('Country/Region').sum()

    df = pd.DataFrame()
    df['Confirmed'] = df_confirmed[date]
    df['Deaths'] = df_deaths[date]
    df['Recovered'] = df_recovered[date]

    return render_template('index.html',
                            date=dt.strptime(date,'%m/%d/%y').strftime('%A, %d, %B, %Y'),
                            fig_html=fig_html,
                            df=df,
                            countries=countries)

@core.route('/info')
def info():
    countries_df = pd.read_csv('../countries.csv')
    countries = countries_df.columns.tolist()
    return render_template('info.html', countries=countries)
