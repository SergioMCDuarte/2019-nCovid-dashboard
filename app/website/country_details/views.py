from flask import render_template, request, Blueprint, redirect, url_for
import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from datetime import datetime as dt, timedelta as td
import math
import json
import csv
data_path = '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'

def create_plot(country):

    df_confirmed = pd\
                .read_csv(data_path+'time_series_covid19_confirmed_global.csv')

    df_confirmed\
        .drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)

    df_deaths = pd.read_csv(data_path+'time_series_covid19_deaths_global.csv')

    df_deaths\
        .drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)

    df_recovered = pd.read_csv(data_path+'time_series_covid19_recovered_global.csv')

    df_recovered\
        .drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)


    df_confirmed_grouped = df_confirmed.groupby('Country/Region').sum().T
    df_deaths_grouped = df_deaths.groupby('Country/Region').sum().T
    df_recovered_grouped = df_recovered.groupby('Country/Region').sum().T

    confirmed_df_country = df_confirmed_grouped[country]
    deaths_df_country = df_deaths_grouped[country]
    recovered_df_country = df_recovered_grouped[country]

    # --- Forecast --- #
    def logistic_func(X,L=1,k=1,x0=0):
        y = []
        for x in X:
            y.append(L/(1+math.exp(-k*(x-x0))))
        return y

    forecast_days = 5

    forecast_dt = []
    for day in range(forecast_days):
        forecast_dt.append(
            (dt.strptime(confirmed_df_country[confirmed_df_country.values>0].index.tolist()[-1],'%m/%d/%y')\
            +td(days=(day+1))).strftime('%-m/%-d/%y'))

    x_dt = confirmed_df_country[confirmed_df_country.values>0].index.tolist() + forecast_dt


    x = [x for x in range(len(confirmed_df_country[confirmed_df_country.values>0]))]
    x_forecast = [x for x in range(len(confirmed_df_country[confirmed_df_country.values>0])+forecast_days)]
    y = confirmed_df_country[confirmed_df_country.values>0].values

    popt, pcov = curve_fit(logistic_func, x, y, p0=[max(y), 1, len(y)/2], maxfev=10000)
    _tmp = logistic_func(x_forecast,popt[0],popt[1],popt[2])
    y_forecast = [int(y) for y in _tmp]

    if (np.isinf(pcov)).any():
        x_dt = x_dt[0],
        y_forecast = [0]
        name = 'Forecast not Available'
    else:
        name = '{} day Forecast - Confirmed Cases'.format(forecast_days)

    #------------------#

    trace0 = go.Scatter(
                    x = confirmed_df_country[confirmed_df_country.values>0].index,
                    y = confirmed_df_country[confirmed_df_country.values>0].values,
                    line={"dash": "dot"},
                    name="Confirmed Cases"
                    )
    trace1 = go.Scatter(
                    x = deaths_df_country[confirmed_df_country.values>0].index,
                    y = deaths_df_country[confirmed_df_country.values>0].values,
                    line={"dash": "dot"},
                    name="Deaths"
                    )
    trace2 = go.Scatter(
                    x = recovered_df_country[confirmed_df_country.values>0].index,
                    y = recovered_df_country[confirmed_df_country.values>0].values,
                    line={"dash": "dot"},
                    name="Recovered"
                    )
    trace3 = go.Scatter(
                    x = x_dt,
                    y = y_forecast,
                    line={"dash": "dashdot"},
                    name=name
                    )

    data_totals = [trace0, trace1, trace2, trace3]

    graphJSON_totals = json.dumps(data_totals, cls=plotly.utils.PlotlyJSONEncoder)

    diff_confirmed_country = []

    for idx, row in enumerate(confirmed_df_country[confirmed_df_country.values>0]):
        if idx == 0:
            diff_confirmed_country.append(0)
            past_value = 0
        else:
            if past_value == 0:
                diff_confirmed_country.append(0)
            else:
                diff_confirmed_country.append(row-past_value)

        past_value = row

    trace1 = go.Bar(
                    x = confirmed_df_country[confirmed_df_country.values>0].index,
                    y = diff_confirmed_country,
                    name=country
                    )

    data_diff = [trace1]

    graphJSON_diff = json.dumps(data_diff, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON_totals, graphJSON_diff

country_details = Blueprint('country_details', __name__)

@country_details.route('/country_details/<country>', methods=["GET"])
def country_details_page(country):
    countries = []
    with open('../countries.csv','r') as csvfile:
        for line in csvfile:
            countries.append(line.split('\n')[0].replace('\"',''))

    if country not in countries:
        return redirect(url_for('core.index'))

    plot_totals, plot_diff = create_plot(country)

    return render_template('country_details.html',
                            plot_totals=plot_totals,
                            plot_diff=plot_diff,
                            country=country,
                            countries=sorted(countries))
