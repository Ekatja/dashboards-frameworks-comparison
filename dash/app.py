# -*- coding: utf-8 -*-

import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import dateutil
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt


app = dash.Dash(__name__)
# app.css.append_css({
#     "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
# })

##############################################################
#                                                            #
#             D  A  T  A     L  O  A  D  I  N  G             #
#                                                            #
##############################################################

#kickstarter_df = pd.read_csv('C:\\Users\\Ekaterina\\Documents\\dashboards-frameworks-comparison\\dash\\kickstarter-cleaned.csv', parse_dates=True)

df = pd.read_csv('C:\\Users\\Ekaterina\\Documents\\dashboards-frameworks-comparison\\dash\\verkaufte_artikel_2018.csv', parse_dates=True)

# kickstarter_df['broader_category'] = kickstarter_df['category_slug'].str.split('/').str.get(0)
# kickstarter_df['created_at'] = pd.to_datetime(kickstarter_df['created_at'])

# kickstarter_df_sub = kickstarter_df.sample(10000)

METRICS = ['Bestellungen', 'Umsatz', 'RE1_abs', 'RE1_rel', 'AvgWarenkorbwert', 'AnzahlArtikelproWarenkorb']
CHANNELS = df.Kanal.unique()
# CATEGORIES = kickstarter_df['broader_category'].unique()
# COLUMNS = ['launched_at', 'deadline', 'blurb', 'usd_pledged', 'state', 'spotlight', 'staff_pick', 'category_slug', 'backers_count', 'country']
# # Picked with http://tristen.ca/hcl-picker/#/hlc/6/1.05/251C2A/E98F55
COLORS = ['#7DFB6D', '#C7B815', '#D4752E', '#C7583F']
# STATES = ['successful', 'suspended', 'failed', 'canceled']


##############################################################
#                                                            #
#                   L  A  Y  O  U  T                         #
#                                                            #
##############################################################


app.layout = html.Div(children=[
    html.H1(children='KPI Dashboard', style={
        'textAlign': 'center',
    }),
    dcc.Dropdown(
        id='channel',
        options=[{'label': i, 'value': i} for i in CHANNELS],
        multi=True,
        value = ['teufel-shop'],
        className = 'dropdown'
    ),
    dcc.Dropdown(
        id='metrics',
        options=[{'label': i, 'value': i} for i in METRICS],
        multi=False,
        value = 'Umsatz',
        className = 'dropdown'
    ),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=dt(2018, 1, 1),
        max_date_allowed=dt(2019, 11, 21),
        initial_visible_month=dt(2018,11, 1),
        display_format='DD/MM/YYYY',
        start_date=dt(2018, 11, 1),
        end_date=dt(2018, 11, 14),
        # end_date=dt.now(),
    ),
    html.Div(id='output-container-date-picker-range'),
    dcc.Graph(
        id='usd-pledged-vs-date',
    ),
    # dcc.Graph(
    #     id='count-state-vs-category',
    # )
])


##############################################################
#                                                            #
#            I  N  T  E  R  A  C  T  I  O  N  S              #
#                                                            #
##############################################################

@app.callback(
    dash.dependencies.Output('output-container-date-picker-range', 'children'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_output(start_date, end_date):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%d')
        start_date_string = start_date.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date = dt.strptime(end_date, '%Y-%m-%d')
        end_date_string = end_date.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix


@app.callback(
    dash.dependencies.Output('usd-pledged-vs-date', 'figure'),
    [
        dash.dependencies.Input('channel', 'value'),
        dash.dependencies.Input('metrics', 'value'),
        dash.dependencies.Input('my-date-picker-range', 'start_date'),
        dash.dependencies.Input('my-date-picker-range', 'end_date'),
    ])
def update_scatterplot(channel, metric, start_date, end_date ):
    if channel is None or channel == []:
        channel = CHANNELS
    print('channel', channel)
    if metric is None or metric == []:
        # metric = METRICS
        metric = 'Bestellungen'
    print('metric', metric)
    sub_df = {}
    traces = {} 
    for c in channel:
        print(c)
        sub_df[c] = df[(df.Kanal == c) & (start_date <= df.Datum) & (df.Datum <= end_date)]
        traces[c] = go.Scatter(x=sub_df[c].Datum, y=sub_df[c][metric], mode='lines', name=c )

    return {
        'data': [ traces[key] for key in channel],
        'layout': go.Layout(
            xaxis={'title': 'Date'},
            yaxis={'title': metric},
            margin={'l': 60, 'b': 40, 't': 50, 'r': 60},
            legend=dict(orientation="h"),
            hovermode='closest'
        )
    }




##############################################################
#                                                            #
#                      M  A  I  N                            #
#                                                            #
##############################################################


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('PRODUCTION') is None
    app.run_server(debug=debug, host='0.0.0.0', port=port)
