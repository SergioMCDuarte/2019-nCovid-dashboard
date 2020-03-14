from flask import render_template, request, Blueprint, redirect, url_for
import plotly
import plotly.graph_objs as go
from datetime import datetime as dt, timedelta as td
import pandas as pd
import numpy as np
import json

world = Blueprint('world', __name__)

@world.route('/world')
def world_page():
    countries_df = pd.read_csv('../countries.csv')
    countries = countries_df.columns.tolist()


    date = (dt.now() - td(days=1)).strftime('%-m/%-d/%y')

    df_confirmed = pd.read_csv(
        '../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv',
        usecols=['Country/Region', date]).groupby('Country/Region').sum()

    df_deaths = pd.read_csv(
        '../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv',
        usecols=['Country/Region', date]).groupby('Country/Region').sum()

    df_recovered = pd.read_csv(
        '../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv',
        usecols=['Country/Region', date]).groupby('Country/Region').sum()

    df = pd.DataFrame()
    df['Confirmed'] = df_confirmed[date]
    df['Deaths'] = df_deaths[date]
    df['Recovered'] = df_recovered[date]

    return render_template('world.html',
                            df=df,
                            countries=countries)
