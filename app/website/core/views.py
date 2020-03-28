from flask import render_template, request, Blueprint, redirect, url_for
import plotly
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
from datetime import datetime as dt, timedelta as td
import os
import codecs
#print(os.getcwd())
data_path = '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'

core = Blueprint('core', __name__)

@core.route('/')
def index():

    basedir = os.getcwd()

    file = codecs.open(basedir+'/website/static/world_map.html', "r", "utf-8")
    fig_html = file.read()

    date = (dt.now() - td(days=1)).strftime('%-m/%-d/%y')

    countries = []
    with open('../countries.csv','r') as csvfile:
        for line in csvfile:
            countries.append(line.split('\n')[0].replace('\"',''))

    df_confirmed = pd.read_csv(data_path+'time_series_covid19_confirmed_global.csv',
        usecols=['Country/Region', date]).groupby('Country/Region').sum()

    df_deaths = pd.read_csv(data_path+'time_series_covid19_deaths_global.csv',
        usecols=['Country/Region', date]).groupby('Country/Region').sum()

    df_recovered = pd.read_csv(data_path+'time_series_covid19_recovered_global.csv',
        usecols=['Country/Region', date]).groupby('Country/Region').sum()

    df = pd.DataFrame()
    df['Confirmed'] = df_confirmed[date]
    df['Deaths'] = df_deaths[date]
    df['Recovered'] = df_recovered[date]

    return render_template('index.html',
                            date=dt.strptime(date,'%m/%d/%y').strftime('%A, %d, %B, %Y'),
                            fig_html=fig_html,
                            df=df,
                            countries=sorted(countries))

@core.route('/info')
def info():
    countries = []
    with open('../countries.csv','r') as csvfile:
        for line in csvfile:
            countries.append(line.split('\n')[0].replace('\"',''))
            
    return render_template('info.html', countries=sorted(countries))
