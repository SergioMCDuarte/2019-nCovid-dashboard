import pandas as pd
import os
import csv

data_path = '../COVID-19/csse_covid_19_data/csse_covid_19_time_series/'

df= pd.read_csv(data_path+'time_series_19-covid-Confirmed.csv')

countries = []
for country in df['Country/Region']:
    if country not in countries:
        countries.append(country)

os.remove('countries.csv')

with open('countries.csv','w') as csvfile:
    country_writer = csv.writer(csvfile, delimiter=',')
    for country in countries:
        country_writer.writerow([country])
