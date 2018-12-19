# -*- coding: utf-8 -*-

import os
import pymysql as sql
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dateutil
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt


app = dash.Dash(__name__)

##############################################################
#                                                            #
#             D  A  T  A     L  O  A  D  I  N  G             #
#                                                            #
##############################################################

# # Connect to mysql database
# connection = sql.connect(user='ekaterina', password='aeLier4tait2yahx', host='127.0.0.1')
# cursor = connection.cursor()
# # Build a SQL query and run it
# query = ("""
#     SELECT 
#         sc.name AS Kanal,
#         DATE(o.shop_order_date) AS Datum,
#         COUNT(DISTINCT o.id) AS Bestellungen,
#         SUM(IF(oa.single_net_price = 0,
#             o.items_net_price,
#             oa.amount*oa.single_net_price)) AS Umsatz,
#         SUM(IF(oa.single_net_price = 0,
#             o.items_net_price,
#             oa.amount*oa.single_net_price)) - SUM(oa.amount*oa.vendor_price_at_vendor_order) AS RE1_abs,
#         (SUM(IF(oa.single_net_price = 0,
#             o.items_net_price,
#             oa.amount*oa.single_net_price)) - SUM(oa.amount*oa.vendor_price_at_vendor_order)) / SUM(IF(oa.single_net_price = 0,
#             o.items_net_price,
#             oa.amount*oa.single_net_price)) AS RE1_rel,
#         SUM(IF(oa.single_net_price = 0,
#             o.items_net_price,
#             oa.amount*oa.single_net_price)) / COUNT(DISTINCT o.id) AS AvgWarenkorbwert,
#         COUNT(oa.vendor_article_number) / COUNT(DISTINCT o.id) AS AnzahlArtikelproWarenkorb
#     FROM
#         rig.order_articles oa
#             JOIN
#         rig.orders o ON o.id = oa.order_id
#             JOIN
#         rig.shop_channels sc ON sc.id = o.shop_channel_id
#     WHERE
#         YEAR(o.shop_order_date) = 2018
#         AND o.status IN ('sent' , 'packaged', 'delivered')
#         AND oa.vendor_price_at_vendor_order > 0
#     GROUP BY o.shop_channel_id , DATE(o.shop_order_date)
#     ;
#     """)
# cursor.execute(query)
# # Store results in a pandas data frame
# df = pd.read_sql(query, connection) 
# # Close cursor
# cursor.close()

df = pd.read_csv('.\\dash\\verkaufte_artikel_2018.csv', parse_dates=True)

#Konstanten
METRICS = ['Bestellungen', 'Umsatz', 'RE1_abs', 'RE1_rel', 'AvgWarenkorbwert', 'AnzahlArtikelproWarenkorb']
CHANNELS = df.Kanal.unique()
COLORS = ['#7DFB6D', '#C7B815', '#D4752E', '#C7583F']
default_shop = 'teufel-shop'
default_metric = 'Umsatz'

app.config['suppress_callback_exceptions']=True

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
        value = [default_shop],
        className = 'dropdown'
    ),
    dcc.Dropdown(
        id='metrics',
        options=[{'label': i, 'value': i} for i in METRICS],
        multi=False,
        value = default_metric,
        className = 'dropdown'
    ),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=dt(2018, 1, 1),
        max_date_allowed=dt.today().date().replace(year=dt.today().year+1),
        initial_visible_month=dt.today().date().replace(day=1),
        display_format='DD/MM/YYYY',
        # start_date=dt.today().date().replace(day=1),
        # end_date=dt.today().date()
        start_date=dt(2018, 11, 1),
        end_date=dt(2018, 11, 10)
    ),
    
    html.Div(id='output-container-date-picker-range'),

    # html.Div(id='data-table'),
    
    dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in df[['Kanal', 'Datum', default_metric]].columns],
        # columns = [{}],
        data=df.to_dict("rows"),
        
        style_header={
        'backgroundColor': 'rgba(117, 99, 79, 0.5)',
        'fontSize': '1.2em',
        'fontFamily': 'sans-serif',
        'fontWeight': 'bold',
        'paddingLeft': '10px'
        },
        style_cell={
            'textAlign': 'left',
            'fontSize': '1em',
            'fontFamily': 'sans-serif',
            'minWidth': '60px', 
            'width': '60px', 
            'maxWidth': '60px',
            'whiteSpace': 'no-wrap',
        },
        style_cell_conditional=[{
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgb(248, 248, 248)'
        }],
        css=[{
        'selector': '.dash-cell',
        'rule': 'padding-left: 10px;'
        }],
    ),
#  html.Div([
#         dcc.Input(
#             id='editing-columns-name',
#             placeholder='Enter a column name...',
#             value='',
#             style={'padding': 10}
#         ),
#         html.Button('Add Column', id='editing-columns-button', n_clicks=0)
#     ], style={'height': 50}),

#     dash_table.DataTable(
#         id='editing-columns',
#         columns=[{
#             'name': 'Column {}'.format(i),
#             'id': 'column-{}'.format(i),
#             'deletable': True,
#             'editable_name': True
#         } for i in range(1, 5)],
#         data=[
#             {'column-{}'.format(i): (j + (i-1)*5) for i in range(1, 5)}
#             for j in range(5)
#         ],
#         editable=True,
#     ),

    dcc.Graph(
        id='usd-pledged-vs-date',
    ),
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

#Update table
@app.callback(
    dash.dependencies.Output('data-table', 'data'),
    # dash.dependencies.Output('data-table', 'columns')
    # dash.dependencies.Output('data-table', 'children'),
    [
        dash.dependencies.Input('channel', 'value'),
        dash.dependencies.Input('metrics', 'value'),
        dash.dependencies.Input('my-date-picker-range', 'start_date'),
        dash.dependencies.Input('my-date-picker-range', 'end_date'),
    ])

def update_table(channel, metric, start_date, end_date ):
    
    if channel is None or channel == []:
        channel = CHANNELS
    #print('channel', channel)
    if metric is None or metric == []:
        metric = default_metric
    print('metric', metric)
    sub_df = {}
    data = [] 
    print('table update channels', channel)
    for c in channel:
        sub_df[c] = df[(df.Kanal == c) & (start_date <= df.Datum) & (df.Datum <= end_date)]
        default_metric = metric
        # print(sub_df[c][['Kanal', 'Datum', metric]])
        data.append(sub_df[c][['Kanal', 'Datum', metric]])
    print(pd.concat(data).to_dict('records'))
        
    return pd.concat(data).to_dict('records')

@app.callback(
    dash.dependencies.Output('data-table', 'columns'),
    [dash.dependencies.Input('metrics', 'value')],
    [dash.dependencies.State('data-table', 'columns')]
     )
def update_columns(metric, existing_columns):
    
    existing_columns[-1]['name'] = metric
    existing_columns[-1]['id'] = metric
    
    return existing_columns
    
#Update graphic
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
        metric = default_metric
    print('metric', metric)
    sub_df = {}
    traces = {} 
    for c in channel:
        #print(c)
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
