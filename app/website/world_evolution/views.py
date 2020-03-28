from flask import render_template, request, Blueprint, redirect, url_for
import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json

def create_plot():

    df_confirmed = pd.read_parquet('website/static/confirmed.parquet')

    df_confirmed\
        .drop(['Province/State', 'Lat', 'Long'], inplace=True, axis=1)

    df_confirmed_grouped = df_confirmed.groupby('Country/Region').sum().T.sum(axis=1)

    trace0 = go.Scatter(
                    x = df_confirmed_grouped.index,
                    y = df_confirmed_grouped.values,
                    line={"dash": "dot"},
                    name='Total'
                    )

    data_totals = [trace0]

    graphJSON_totals = json.dumps(data_totals, cls=plotly.utils.PlotlyJSONEncoder)

    diff_confirmed = []

    for idx, row in enumerate(df_confirmed_grouped):
        if idx == 0:
            diff_confirmed.append(0)
            past_value = 0
        else:
            if past_value == 0:
                diff_confirmed.append(0)
            else:
                diff_confirmed.append(row-past_value)

        past_value = row


    trace1 = go.Bar(
                    x = df_confirmed_grouped.index,
                    y = diff_confirmed,
                    name='Total'
                    )

    data_diff = [trace1]

    graphJSON_diff = json.dumps(data_diff, cls=plotly.utils.PlotlyJSONEncoder)

    growth_rate = []

    for idx, row in enumerate(diff_confirmed):
        if idx == 0:
            growth_rate.append(0)
            past_value = 0
        else:
            if past_value == 0:
                growth_rate.append(0)
            else:
                growth_rate.append(row/past_value)

        past_value = row

        trace2 = go.Bar(
                        x = df_confirmed_grouped.index,
                        y = growth_rate,
                        name='Total'
                        )

        data_growth = [trace2]

        graphJSON_growth = json.dumps(data_growth, cls=plotly.utils.PlotlyJSONEncoder)


    return graphJSON_totals, graphJSON_diff, graphJSON_growth


world_evolution = Blueprint('world_evolution', __name__)

@world_evolution.route('/world_comparison')
def world_evolution_page():
    countries = []
    with open('../countries.csv','r') as csvfile:
        for line in csvfile:
            countries.append(line.split('\n')[0].replace('\"',''))

    plot_totals, plot_diff, plot_growth = create_plot()
    return render_template('world_evolution.html',
                            plot_totals=plot_totals,
                            plot_diff=plot_diff,
                            plot_growth=plot_growth,
                            countries=sorted(countries))
