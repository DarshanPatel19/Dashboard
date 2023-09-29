from dash import Dash, dcc, html, Input, Output, dash_table
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os
from dateutil.relativedelta import relativedelta
import time

assets_path = os.getcwd() + '/assets'

app = Dash(__name__,
        title='Seasonality',
        assets_folder=assets_path, include_assets_files=True,
        suppress_callback_exceptions=True,
        external_stylesheets=[dbc.themes.LITERA],
        meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
        )


app.layout = html.Div([
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Trending Days Streak Input'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Enter Number of Streak'), width=4, align='left'),
        dbc.Col(html.H6('Select Weeks'), width=4, align='left'),
    ]),
    
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Input(id='trendingstreak_value',
                                type='number', value=10,
                                placeholder='Enter Number of Trades',
                                style={'width': '250px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
                        align='left',width=4,
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='trendingstreak_weekinput',
                                      min=1, max=5,step=1,
                                      marks={str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(1, 6)},
                                      dots=False, updatemode='drag',
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      value=1, included=False,
                                      persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=4, align='left'
        ),
    ]),

    html.Br(),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select type'), width=4, align='left'),
        dbc.Col(html.H6('Select Months'), width=4, align='left'),
       ]),

    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='trendingstreak_type',
                           inline=True,
                           options=[dict(label='bearish', value='less'),
                                    dict(label='bullish', value='more')],
                           value='less',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
                         align='left',width=4,
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='trendingstreak_monthinput',
                                      min=1, max=12,step=1,
                                      marks={str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(1, 13)},
                                      dots=False, updatemode='drag',
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      value=1, included=False,
                                      persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=4, align='left'
        ),
    ]),

    html.Br(),
    html.Br(),
    
    dbc.Row([
        dbc.Col(html.H6('Enter Percentage'), width=4, align='left'),
        dbc.Col(html.H6('Select Years'), width=4, align='left'),
    ]),

    dbc.Row([                
        dbc.Col(
            html.Div([dcc.Input(id='trendingstreak_percent',
                                type='number', value=0,
                                style={'width': '250px', 'height': '30px'},
                                min=-50, step=0.1,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
                    width=4,
                    align='left'
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='trendingstreak_yearinput',
                                      min=1, max=5,step=1,
                                      marks={str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(1, 6)},
                                      dots=False, updatemode='drag',
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      value=1, included=False,
                                      persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=4, align='left'
        ),

    ]),


    html.Br(),
    html.Br(),
    
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Trending Days Streak Output'),
html.Br(),
    
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='trendingstreak_table',
                                           columns = [    
                                                    {"name": ["STREAK","StartDate"], "id": "StartDate"},
                                                    {"name": ["STREAK","StartClose"], "id": "StartClose"},
                                                    {"name": ["STREAK","EndDate"], "id": "EndDate"},
                                                    {"name": ["STREAK","EndClose"], "id": "EndClose"},
                                                    {"name": ["STREAK","TotalDays"], "id": "TotalDays"},
                                                    {"name": ["STREAK","PercentChange"], "id": "PercentChange"},
                                                    {"name": ["WEEK","Date"], "id": "WeekDate"},
                                                    {"name": ["WEEK","Close"], "id": "WeekClose"},
                                                    {"name": ["WEEK","Percent"], "id": "WeekPercent"},
                                                    {"name": ["MONTH","Date"], "id": "MonthDate"},
                                                    {"name": ["MONTH","Close"], "id": "MonthClose"},
                                                    {"name": ["MONTH","Percent"], "id": "MonthPercent"},
                                                    {"name": ["YEAR","Date"], "id": "YearDate"},
                                                    {"name": ["YEAR","Close"], "id": "YearClose"},
                                                    {"name": ["YEAR","Percent"], "id": "YearPercent"},
                                                ],
                                           merge_duplicate_headers=True,
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[
                                            {
                                                'if': {'column_id': colname},
                                                'border-right': '3px solid black'
                                            } for colname in ['PercentChange','WeekPercent','MonthPercent']
                                           ],
                                           style_cell=dict(
                                               whiteSpace='pre-line'
                                           ),
                                           style_header=dict(
                                               width='8px', minWidth='8px', maxWidth='8px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold'
                                                ,textAlign='center'
                                           ),
                                           
                                           style_data=dict(
                                               width='8px', minWidth='8px', maxWidth='8px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='white', color='black',textAlign='center'
                                           )),],
                    style=dict(overflowX='auto', width='100%')),
            width=12, align='center'
        ),    

    ]),

    html.Br(),
    html.Br(),
    html.Br(),


],
 style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)



@app.callback(
    Output(component_id='trendingstreak_table', component_property='data'),
    [Input('trendingstreak_value', 'value'),
     Input('trendingstreak_type','value'),
     Input('trendingstreak_percent','value'), 
     Input('trendingstreak_weekinput', 'value'),
     Input('trendingstreak_monthinput','value'),
     Input('trendingstreak_yearinput','value'), 
    ]      
)
def generate_performance_table(nTrades,opt,percentChange,nweek,nmonth,nyear):
    df = pd.read_csv('./Symbols/ACC/1_Daily.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
    df = df.dropna()

    def addNone(lst,idx,typeN):
        for i in range(len(lst) - idx):
            result[f'{typeN}Date'].append(None)
            result[f'{typeN}Close'].append(None)
            result[f'{typeN}Percent'].append(None)

    def foundDate(typeN,currDate,currClose,idx,sClose):
        result[f'{typeN}Date'].append(currDate.date())
        result[f'{typeN}Close'].append(currClose)
        pc_week = ((currClose - sClose[idx])/sClose[idx])*100
        result[f'{typeN}Percent'].append(pc_week)

    if nTrades is None or nTrades == 0 or percentChange is None:
        return None

    consecutive_count = 0
    result = {
        'StartDate': [],
        'StartClose': [],
        'EndDate': [],
        'EndClose': [],
        'TotalDays': [],
        'PercentChange': [],
        'WeekDate': [],
        'WeekClose': [],
        'WeekPercent': [],
        'MonthDate': [],
        'MonthClose': [],
        'MonthPercent': [],
        'YearDate': [],
        'YearClose': [],
        'YearPercent': []
    }
    weekList = []
    weekIndex = 0
    monthList = []
    monthIndex = 0
    yearList = []
    yearIndex = 0
    dateFound = False
    sClose = []

    
    for index, row in df.iterrows():
        if (row['ReturnPercentage'] < percentChange and opt == 'less') or (row['ReturnPercentage'] > percentChange and opt == 'more'):
            consecutive_count += 1
            if consecutive_count == 1:
                startDate = row['Date']
                startClose = row['Close']
        else:
            if consecutive_count >= nTrades:     
                row_date =row['Date']
                weekList.append(row_date + relativedelta(weeks=nweek))
                monthList.append(row_date + relativedelta(months=nmonth)- relativedelta(days=1))
                yearList.append(row_date + relativedelta(years=nyear) - relativedelta(days=1))
                
                sClose.append(row['Close'])
                if dateFound == False:
                    dateFound = True

                result['StartDate'].append(startDate.date())
                result['StartClose'].append(startClose)
                result['EndDate'].append(row['Date'].date())
                result['EndClose'].append(row['Close'])
                result['TotalDays'].append(consecutive_count)
                pc = ((row['Close'] - startClose)/startClose)*100
                result['PercentChange'].append(pc)

            consecutive_count = 0

        if(dateFound):    
            if weekIndex < len(weekList) and row['Date'] > weekList[weekIndex]:
                foundDate('Week',currDate,currClose,weekIndex,sClose)
                weekIndex += 1
            
            if monthIndex < len(monthList) and row['Date'] > monthList[monthIndex]:
                foundDate('Month',currDate,currClose,monthIndex,sClose)
                monthIndex += 1
            
            if yearIndex < len(yearList) and row['Date'] > yearList[yearIndex]:
                foundDate('Year',currDate,currClose,yearIndex,sClose)
                yearIndex += 1
            
            #Update Current Date and Close
            currDate = row['Date']
            currClose = row['Close']

            # Append None values when no more dates in one_weekList
            if df.index.max() == index:
                addNone(weekList,weekIndex,'Week')
                addNone(monthList,monthIndex,'Month')
                addNone(yearList,yearIndex,'Year')
            

    finaldf = pd.DataFrame.from_dict(result)
    finaldf[['PercentChange','WeekPercent','MonthPercent','YearPercent']] = finaldf[['PercentChange','WeekPercent','MonthPercent','YearPercent']].round(2)
    

    return finaldf.to_dict('records') 


if __name__ == '__main__':
    app.run_server(debug=True)