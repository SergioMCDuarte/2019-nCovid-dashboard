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
    countries = []
    with open('../countries.csv','r') as csvfile:
        for line in csvfile:
            countries.append(line.split('\n')[0].replace('\"',''))

    df = pd.read_parquet('website/static/confirmed.parquet')
    date = (dt.now() - td(days=1)).strftime('%-m/%-d/%y') if \
                    (dt.now() - td(days=1)).strftime('%-m/%-d/%y') in df.columns \
                    else list(df.columns)[-1]

    df = pd.DataFrame()

    df_confirmed = pd.read_parquet('website/static/confirmed.parquet',
        columns=['Country/Region', date]).groupby('Country/Region').sum()

    df_deaths = pd.read_parquet('website/static/deaths.parquet',
        columns=['Country/Region', date]).groupby('Country/Region').sum()

    df_recovered = pd.read_parquet('website/static/recovered.parquet',
        columns=['Country/Region', date]).groupby('Country/Region').sum()

    df['Confirmed'] = df_confirmed[date]
    df['Deaths'] = df_deaths[date]
    df['Recovered'] = df_recovered[date]

    return render_template('world.html',
                            df=df,
                            countries=sorted(countries))
