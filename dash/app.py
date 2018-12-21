# -*- coding: utf-8 -*-

import os
import pymysql as sql
import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dateutil
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt
import dotenv
import os


DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
USERNAME = os.getenv("USERNAME")
DASHBOARDPASS = os.getenv("DASHBOARDPASS")
# Keep this out of source code repository - save in a file or a database
# VALID_USERNAME_PASSWORD_PAIRS = [
#     ['USERNAME', 'DASHBOARDPASS']
# ]

#Login and pass for dashboard
VALID_USERNAME_PASSWORD_PAIRS = [
    ['fla', 'test']
]
print(DATABASE_USER)
# external_stylesheets = ['hier ein Link']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app = dash.Dash(__name__)

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

##############################################################
#                                                            #
#             D  A  T  A     L  O  A  D  I  N  G             #
#                                                            #
##############################################################

# # Connect to mysql database
# connection = sql.connect(user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST)
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
df[['RE1_rel', 'AvgWarenkorbwert','AnzahlArtikelproWarenkorb']] = df[['RE1_rel', 'AvgWarenkorbwert','AnzahlArtikelproWarenkorb']].apply(lambda x: round(x, 2))
df['Datum'] = pd.to_datetime(df['Datum'], format='%Y-%m-%d')


#Konstanten
METRICS = ['Bestellungen', 'Umsatz', 'RE1_abs', 'RE1_rel', 'AvgWarenkorbwert', 'AnzahlArtikelproWarenkorb']
CHANNELS = df.Kanal.unique()
COLORS = ['#7DFB6D', '#C7B815', '#D4752E', '#C7583F']
default_shop = 'teufel-shop'
default_metric = 'Umsatz'

exportfilename = 'export-data.csv'

app.config['suppress_callback_exceptions']=True

##############################################################
#                                                            #
#                   L  A  Y  O  U  T                         #
#                                                            #
##############################################################


app.layout = html.Div(children=[
    html.H1(
        children='KPI Dashboard', 
        style={
        'textAlign': 'center',
        }
    ),
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
        end_date=dt(2018, 11, 10),
        
    ),
    # html.Div(id='output-container-date-picker-range'),
    dcc.Graph(
        id='metric-vs-date',
        style={
            'width': '96%',
            'marginTop': '20px',
            'marginBottom' : '40px',
            'fontFamily': 'sans-serif',
            'fontSize' : '14px',
            'height' : '470px'
            },
    ),
    dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in df[['Kanal', 'Datum', default_metric]].columns],
        data=df.to_dict("rows"),
        # sorting=True,
        # sorting_type="multi",
        
        style_header={
        'backgroundColor': 'rgba(117, 99, 79, 0.5)',
        'fontSize': '1.2em',
        'fontFamily': 'sans-serif',
        'fontWeight': 'bold',
        # 'paddingLeft': '10px'
        },
        style_cell={
            'textAlign': 'left',
            'fontSize': '1em',
            'fontFamily': 'sans-serif',
            'minWidth': '60px', 
            'width': '60px', 
            'maxWidth': '60px',
            'whiteSpace': 'no-wrap',
            'paddingLeft' : '10px',
        },
        style_cell_conditional=[{
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgb(248, 248, 248)'
        }],
        # css=[{
        # 'selector': '.dash-cell',
        # 'rule': 'padding-left: 10px;'
        # }],
    ),
    
    html.Div([
       html.Button('Export as CSV', id='export-button'),
    #    html.P(id='editable-table-hidden', style={'display':'none'}),
       html.P(id='save-button-hidden', style={'display':'none'}),
    ])
])


def filter_data(channel, metric, start_date, end_date):
    
    sub_df = df[(df.Kanal == channel) & (df.Datum >= start_date) & (df.Datum <= end_date)][['Kanal', 'Datum', metric]]
    return sub_df

def format_data(data):
    #Format date column
    
    data['Datum'] = pd.to_datetime(data['Datum'], format='%Y-%m-%d')
    data['Datum'] = data['Datum'].dt.strftime('%d/%m/%Y')
    #format last column with metrics depends on column name
    if(data.columns[-1] in ['Umsatz', 'RE1_abs', 'AvgWarenkorbwert']):
        data[data.columns[-1]] = data[data.columns[-1]].map('{:.2f}€'.format)
    elif(data.columns[-1] == 'RE1_rel'):
        data[data.columns[-1]] = (data[data.columns[-1]]*100).map('{:.2f}%'.format)

##############################################################
#                                                            #
#            I  N  T  E  R  A  C  T  I  O  N  S              #
#                                                            #
##############################################################

# @app.callback(
#     dash.dependencies.Output('output-container-date-picker-range', 'children'),
#     [dash.dependencies.Input('my-date-picker-range', 'start_date'),
#      dash.dependencies.Input('my-date-picker-range', 'end_date')])

# def update_output(start_date, end_date):
#     string_prefix = 'You have selected: '
#     if start_date is not None:
#         start_date = dt.strptime(start_date, '%Y-%m-%d')
#         start_date_string = start_date.strftime('%B %d, %Y')
#         string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
#     if end_date is not None:
#         end_date = dt.strptime(end_date, '%Y-%m-%d')
#         end_date_string = end_date.strftime('%B %d, %Y')
#         string_prefix = string_prefix + 'End Date: ' + end_date_string
#     if len(string_prefix) == len('You have selected: '):
#         return 'Select a date to see it displayed here'
#     else:
#         return string_prefix

#Update table
@app.callback(
    dash.dependencies.Output('data-table', 'data'),
    [dash.dependencies.Input('channel', 'value'),
    dash.dependencies.Input('metrics', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date'),
    dash.dependencies.Input('export-button', 'n_clicks'),
    ])

def update_table(channel, metric, start_date, end_date, n_clicks ):
    print(n_clicks)
    if channel is None or channel == []:
        channel = CHANNELS
    
    if metric is None or metric == []:
        metric = default_metric
    
    sub_df = {}
    data = [] 
    for c in channel:
        sub_df[c] = filter_data(c, metric, start_date, end_date)
        data.append(sub_df[c])
    result = pd.concat(data)
    # Click on export button
    if(n_clicks is not None):
        result.to_csv(exportfilename, index=False, encoding='utf-8')
    #Format data for show in table
    format_data(result)        
    return result.to_dict('records')

#Update columns
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
    dash.dependencies.Output('metric-vs-date', 'figure'),
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
        
        sub_df[c] = df[(df.Kanal == c) & (start_date <= df.Datum) & (df.Datum <= end_date)]
        traces[c] = go.Scatter(x=sub_df[c].Datum, y=sub_df[c][metric], mode='lines', name=c )

    return {
        'data': [ traces[key] for key in channel],
        'layout': go.Layout(
            xaxis={'title': 'Datum'},
                         yaxis={'title': metric},
            margin={'l': 60, 'b': 50, 't': 20, 'r': 60},
            legend=dict(orientation="h", x=0, y=-0.2),
            hovermode='closest',
            font=dict(family='sans-serif', size=14)
        )
    }

#Save datatable as csv
# @app.callback(dash.dependencies.Output('save-button-hidden', 'children'),
#              [dash.dependencies.Input('export-button', 'n_clicks')],
#              [dash.dependencies.State('data-table', 'data')]
#               )

# def save_current_table(savebutton, channels, metric, start_date, end_date):
#     table_df = filter_data(channels, metric, start_date, end_date)
#     print('tablerows', table_df)

#     # table_df = pd.DataFrame(rows) #convert current rows into df

#     # if selected_row_indices:
#     #     table_df = table_df.loc[selected_row_indices] #filter according to selected rows

#     if savebutton:
#         print('i am save button')
#         table_df.to_csv(exportfilename, index=False, encoding='utf-8')
#         return "Current table saved."

##############################################################
#                                                            #
#                      M  A  I  N                            #
#                                                            #
##############################################################

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('PRODUCTION') is None
    app.run_server(debug=debug, host='0.0.0.0', port=port)
