# -*- coding: utf-8 -*-

import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import dateutil
import plotly.graph_objs as go
import pandas as pd


app = dash.Dash()
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

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
        multi=True
    ),
    dcc.Dropdown(
        id='metrics',
        options=[{'label': i, 'value': i} for i in METRICS],
        multi=True
    ),
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
    dash.dependencies.Output('usd-pledged-vs-date', 'figure'),
    [
        dash.dependencies.Input('channel', 'value'),
        dash.dependencies.Input('metrics', 'value'),
    ])
def update_scatterplot(channel, metric ):
    if channel is None or channel == []:
        channel = CHANNELS
    
    if metric is None or metric == []:
        # metric = METRICS
        metric = 'Bestellungen'

    sub_df_x = df[(df.Kanal.isin(channel))]
    sub_df_y = df[(df.Kanal.isin(channel))][metric]

    return {
        'data': [
            go.Scatter(
                x=sub_df_x.Datum,
                y=sub_df_y,
                # text=sub_df[(kickstarter_df_sub.state == state)]['name'],
                mode='lines',
                opacity=0.7,
                # marker={
                #     'size': 15,
                #     'color': color,
                #     'line': {'width': 0.5, 'color': 'white'}
                # },
                # name=state,
            ) 
            # for (state, color) in zip(STATES, COLORS)
        ],
        'layout': go.Layout(
            xaxis={'title': 'Date'},
            yaxis={'title': 'USD pledged'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


# @app.callback(
#     dash.dependencies.Output('count-state-vs-category', 'figure'),
#     [
#         dash.dependencies.Input('categories', 'value'),
#         dash.dependencies.Input('usd-pledged-vs-date', 'relayoutData')
#     ])
# def update_bar_chart(categories, relayoutData):
#     if categories is None or categories == []:
#         categories = CATEGORIES

#     if (relayoutData is not None
#             and (not (relayoutData.get('xaxis.autorange') or relayoutData.get('yaxis.autorange')))):
#         x0 = dateutil.parser.parse(relayoutData['xaxis.range[0]'])
#         x1 = dateutil.parser.parse(relayoutData['xaxis.range[1]'])
#         y0 = 10 ** relayoutData['yaxis.range[0]']
#         y1 = 10 ** relayoutData['yaxis.range[1]']

#         sub_df = kickstarter_df[kickstarter_df.created_at.between(x0, x1) & kickstarter_df.usd_pledged.between(y0, y1)]
#     else:
#         sub_df = kickstarter_df

#     stacked_barchart_df = (
#         sub_df[sub_df['broader_category'].isin(categories)]['state'].groupby(sub_df['broader_category'])
#         .value_counts(normalize=False)
#         .rename('count')
#         .to_frame()
#         .reset_index('state')
#         .pivot(columns='state')
#         .reset_index()
#     )
#     return {
#         'data': [
#             go.Bar(
#                 x=stacked_barchart_df['broader_category'],
#                 y=stacked_barchart_df['count'][state],
#                 name=state,
#                 marker={
#                     'color': color
#                 }
#             ) for (state, color) in zip(STATES[::-1], COLORS[::-1])
#         ],
#         'layout': go.Layout(
#             yaxis={'title': 'Number of projects'},
#             barmode='stack',
#             hovermode='closest'
#         )
#     }

##############################################################
#                                                            #
#                      M  A  I  N                            #
#                                                            #
##############################################################


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('PRODUCTION') is None
    app.run_server(debug=debug, host='0.0.0.0', port=port)
