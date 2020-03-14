from flask import render_template, request, Blueprint, redirect, url_for
import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json
data_path = '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'

def create_plot(country):

    df_confirmed = pd\
                .read_csv(data_path+'time_series_19-covid-Confirmed.csv')

    df_confirmed\
        .drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)

    df_deaths = pd.read_csv(data_path+'time_series_19-covid-Deaths.csv')

    df_deaths\
        .drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)

    df_recovered = pd.read_csv(data_path+'time_series_19-covid-Recovered.csv')

    df_recovered\
        .drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)


    df_confirmed_grouped = df_confirmed.groupby('Country/Region').sum().T
    df_deaths_grouped = df_deaths.groupby('Country/Region').sum().T
    df_recovered_grouped = df_recovered.groupby('Country/Region').sum().T

    confirmed_df_country = df_confirmed_grouped[country]
    deaths_df_country = df_deaths_grouped[country]
    recovered_df_country = df_recovered_grouped[country]

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

    data_totals = [trace0, trace1, trace2]

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

    trace1 = go.Scatter(
                    x = confirmed_df_country[confirmed_df_country.values>0].index,
                    y = diff_confirmed_country,
                    line={"dash": "dot"},
                    name=country
                    )

    data_diff = [trace1]

    graphJSON_diff = json.dumps(data_diff, cls=plotly.utils.PlotlyJSONEncoder)

    growth_rate = []

    for idx, row in enumerate(diff_confirmed_country):
        if idx == 0:
            growth_rate.append(0)
            past_value = 0
        else:
            if past_value == 0:
                growth_rate.append(0)
            else:
                growth_rate.append(row/past_value)

        past_value = row

        trace2 = go.Scatter(
                        x = confirmed_df_country[confirmed_df_country.values>0].index,
                        y = growth_rate,
                        line={"dash": "dot"},
                        name=country
                        )

        data_growth = [trace2]

        graphJSON_growth = json.dumps(data_growth, cls=plotly.utils.PlotlyJSONEncoder)


    return graphJSON_totals, graphJSON_diff, graphJSON_growth

country_details = Blueprint('country_details', __name__)

@country_details.route('/country_details/<country>', methods=["GET"])
def country_details_page(country):
    plot_totals, plot_diff, plot_growth = create_plot(country)
    countries_df = pd.read_csv('../countries.csv')
    countries = countries_df.columns.tolist()
    return render_template('country_details.html',
                            plot_totals=plot_totals,
                            plot_diff=plot_diff,
                            plot_growth=plot_growth,
                            country=country,
                            countries=countries)
