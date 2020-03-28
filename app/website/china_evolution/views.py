from flask import render_template, request, Blueprint, redirect, url_for
import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json
data_path = '../../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'

def create_plot():
    df_confirmed = pd\
                .read_csv(data_path+'time_series_covid19_confirmed_global.csv')

    df_confirmed\
        .drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)

    df_confirmed_grouped = df_confirmed.groupby('Country/Region').sum().T

    confirmed_df_china = df_confirmed_grouped['China']
    confirmed_df_not_china = df_confirmed_grouped.drop('China', axis=1).sum(axis=1)

    trace0 = go.Scatter(
                    x = confirmed_df_china.index,
                    y = confirmed_df_china.values,
                    line={"dash": "dot"},
                    name='China'
                    )
    trace1 = go.Scatter(
                    x = confirmed_df_not_china.index,
                    y = confirmed_df_not_china.values,
                    line={"dash": "dot"},
                    name='Not China'
                )

    data_totals = [trace0, trace1]

    graphJSON_totals = json.dumps(data_totals, cls=plotly.utils.PlotlyJSONEncoder)

    diff_confirmed_china = []

    for idx, row in enumerate(confirmed_df_china):
        if idx == 0:
            diff_confirmed_china.append(0)
            past_value = 0
        else:
            if past_value == 0:
                diff_confirmed_china.append(0)
            else:
                diff_confirmed_china.append(row-past_value)

        past_value = row

    diff_confirmed_not_china = []

    for idx, row in enumerate(confirmed_df_not_china):
        if idx == 0:
            diff_confirmed_not_china.append(0)
            past_value = 0
        else:
            if past_value==0:
                diff_confirmed_not_china.append(0)
            else:
                diff_confirmed_not_china.append(row-past_value)

        past_value = row

    trace2 = go.Scatter(
                    x = confirmed_df_china.index,
                    y = diff_confirmed_china,
                    line={"dash": "dot"},
                    name='China'
                    )
    trace3 = go.Scatter(
                    x = confirmed_df_not_china.index,
                    y = diff_confirmed_not_china,
                    line={"dash": "dot"},
                    name='Not China'
                )

    data_diff = [trace2, trace3]

    graphJSON_diff = json.dumps(data_diff, cls=plotly.utils.PlotlyJSONEncoder)

    growth_rate_china = []

    for idx, row in enumerate(diff_confirmed_china):
        if idx == 0:
            growth_rate_china.append(0)
            past_value = 0
        else:
            if past_value == 0:
                growth_rate_china.append(0)
            else:
                growth_rate_china.append(row/past_value)

        past_value = row

    growth_rate_not_china = []

    for idx, row in enumerate(diff_confirmed_not_china):
        if idx == 0:
            growth_rate_not_china.append(0)
            past_value = 0
        else:
            if past_value == 0:
                growth_rate_not_china.append(0)
            else:
                growth_rate_not_china.append(row/past_value)

        past_value = row

        trace4 = go.Scatter(
                        x = confirmed_df_china.index,
                        y = growth_rate_china,
                        line={"dash": "dot"},
                        name='China'
                        )
        trace5 = go.Scatter(
                        x = confirmed_df_not_china.index,
                        y = growth_rate_not_china,
                        line={"dash": "dot"},
                        name='Not China'
                    )

        data_growth = [trace4, trace5]

        graphJSON_growth = json.dumps(data_growth, cls=plotly.utils.PlotlyJSONEncoder)


    return graphJSON_totals, graphJSON_diff, graphJSON_growth


china_evolution = Blueprint('china_evolution', __name__)

@china_evolution.route('/china_comparison')
def china_evolution_page():
    countries = []
    with open('../countries.csv','r') as csvfile:
        for line in csvfile:
            countries.append(line.split('\n')[0])

    plot_totals, plot_diff, plot_growth = create_plot()
    return render_template('china_evolution.html',
                            plot_totals=plot_totals,
                            plot_diff=plot_diff,
                            plot_growth=plot_growth,
                            countries=sorted(countries))
