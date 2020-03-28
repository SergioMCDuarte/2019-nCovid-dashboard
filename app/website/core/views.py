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
import requests
#print(os.getcwd())

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

    df_confirmed = pd.read_parquet('website/static/confirmed.parquet',
        columns=['Country/Region', date]).groupby('Country/Region').sum()

    df_deaths = pd.read_parquet('website/static/deaths.parquet',
        columns=['Country/Region', date]).groupby('Country/Region').sum()

    df_recovered = pd.read_parquet('website/static/recovered.parquet',
        columns=['Country/Region', date]).groupby('Country/Region').sum()

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

@core.route('/search', methods=["GET", "POST"])
def search():
    countries = []
    with open('../countries.csv','r') as csvfile:
        for line in csvfile:
            countries.append(line.split('\n')[0].replace('\"',''))

    query = [item for item in request.args.items()][0][1]

    possible_query = []

    for country in countries:
        if query.lower() in country.lower():
            possible_query.append(country)

    if len(possible_query) < 1:
        return render_template('country_not_found.html')
    elif len(possible_query) == 1:
        return redirect(url_for('country_details.country_details_page', country=possible_query[0]))
    else:
        return render_template('search.html', countries=sorted(countries), possible_query=possible_query)
