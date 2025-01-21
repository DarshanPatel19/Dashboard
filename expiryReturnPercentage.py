from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
from itertools import zip_longest
import random
import os
from math import floor, ceil

expiryDatatableToDownload = pd.DataFrame()
expiryDistributionDatatableToDownload = pd.DataFrame()
assets_path = os.getcwd() + '/assets'


app = Dash(__name__,
           title='Seasonality',
           assets_folder=assets_path, include_assets_files=True,
           suppress_callback_exceptions=True,
           external_stylesheets=[dbc.themes.LITERA],
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
           )

app.layout = html.Div([
    html.Br(), html.Br(),

    # Election Year Inputs
    html.H2('Expiry Day Inputs'),
    html.Br(),
    dbc.Row([
         dbc.Col(html.H6('Select Symbol'), width=5, align='left'),
         dbc.Col(html.H6('Select Date Range'), width=5, align='left'),
        
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_expirySymbolNameToPlot',
                                   options=['BANKNIFTY', 'SENSEX', 'NIFTY', 'FINNIFTY', 'BANKEX', 'MIDCPNIFTY'],
                                   value='BANKNIFTY',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='50%')),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.DatePickerRange(id='daily_expiryDateRange',
                                min_date_allowed=date(1900, 1, 1), max_date_allowed=date(2025, 12, 31),
                                start_date=date(2016, 1, 1), end_date=date(2023, 12, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    
    dbc.Row([
        dbc.Col(html.H6('Select Expiry Day Type'), width=5, align='left'),
        dbc.Col(html.H6('Select Expiry Day'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_expiryDayType',
                           inline=True,
                           options=[dict(label='All Expiries', value=0),
                                    dict(label='Latest Expiry', value=1),
                                   ],
                           value=0,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_expiryDay',
                        inline=True,
                        options=[   
                                    dict(label='Disable', value=-1),
                                    dict(label='Monday', value=0),
                                    dict(label='Tuesday', value=1),
                                    dict(label='Wednesday', value=2),
                                    dict(label='Thursday', value=3),
                                    dict(label='Friday', value=4),
                                ],
                        value=-1,
                        className='radiobutton-group',
                        persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
    ]),
    
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Return Percentage Basis'), width=5, align='left'),
        dbc.Col(html.H6('Select Month'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
             dcc.RadioItems(id='daily_expiryReturnPercentageBasis',
                           inline=True,
                           options=[dict(label='Close-To-Close', value=0),
                                    dict(label='Open-To-Close', value=1),
                                    dict(label='High-To-Low', value=2)],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'        
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_expiryReturnPercentageMonth',
                                   options=['All', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                                   value='All',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='50%')),
            width=5, align='left'
        ),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Return Percentage Range'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.RangeSlider(id='daily_expiryReturnPercentageRange',
                                 min=-5, max=5, step=0.5,
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='top'),
                                 included=False,
                                 value=[0,0],
                                 persistence=True, persistence_type='session')],
                     style=dict(width='100%')),
                width=8, align='left'
        ),
    ]),
    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.Br(),
    
    html.H4("Expiry Day Returns"),
    html.Br(),
    dbc.Button(id='daily_expiryDatatable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
    ),
    dcc.Download(id='daily_expiryDatatable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([
                dash_table.DataTable(id='daily_expiryDatatable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           columns=[
                                                    {'name': 'Month', 'id': 'Month'},
                                                    {'name': 'ExpiryWeekNumber 1', 'id': '1'},
                                                    {'name': 'ExpiryWeekNumber 2', 'id': '2'},
                                                    {'name': 'ExpiryWeekNumber 3', 'id': '3'},
                                                    {'name': 'ExpiryWeekNumber 4', 'id': '4'},
                                                    {'name': 'ExpiryWeekNumber 5', 'id': '5'}
                                            ],
                                           style_data_conditional=
                                            [
                                               {
                                               'if': {
                                                   'column_id': 'Month',
                                                },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold',
                                               'minWidth': '150px',
                                               'maxWidth': '150px'
                                                },
                                            ],
                                           style_cell=dict(
                                               whiteSpace='pre-line',
                                               minWidth='60px', maxWidth='150px',
                                               overflow = 'hidden', #textOverflow = 'ellipsis',
                                               textAlign= 'center',
                                           ),
                                           style_header=dict(
                                               minWidth='60px', maxWidth='150px',
                                               overflow='hidden', #textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold',
                                               textAlign='center'
                                           ),
                                           style_data=dict(
                                               minWidth='60px', maxWidth='150px',
                                               overflow='hidden', #textOverflow='ellipsis',
                                               backgroundColor='white', color='black',
                                               textAlign='center',
                                           ),
                    ),
                    ],
                        style=dict(width='100%', overFlowX='scroll')
            ),
            width=12, align='left'
        )
    ]),
    html.Br(),
      dbc.Row([
        dbc.Col(html.H6('Enter Interval for Returns Distribution'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Input(id='daily_expiryReturnsDistributionInterval',
                                type='number',
                                style={'width': '250px', 'height': '30px'},
                                min=0.1, value=0.5,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=5, align='left'
        ),
    ]),
    html.Br(),
    html.H4("Expiry Day Returns Distribution"),
    html.Br(),
    dbc.Button(id='daily_expiryDayReturnsDistributionDatatable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
    ),
    dcc.Download(id='daily_expiryDayReturnsDistributionDatatable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([
                dash_table.DataTable(id='daily_expiryDayReturnsDistributionDatatable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=
                                            [
                                               {
                                               'if': {
                                                   'column_id': 'Returns Frequency',
                                                },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold',
                                               'minWidth': '150px',
                                               'maxWidth': '150px',
                                                },
                                            ],
                                           style_cell=dict(
                                               whiteSpace='pre-line',
                                               minWidth='60px', maxWidth='150px',
                                               overflow = 'hidden', #textOverflow = 'ellipsis',
                                               textAlign= 'center',
                                           ),
                                           style_header=dict(
                                               minWidth='60px', maxWidth='150px',
                                               overflow='hidden', #textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold',
                                               textAlign='center'
                                           ),
                                           style_data=dict(
                                               minWidth='60px', maxWidth='150px',
                                               overflow='hidden', #textOverflow='ellipsis',
                                               backgroundColor='white', color='black',
                                               textAlign='center',
                                           ),
                    ),
                    ],
                        style=dict(width='100%', overFlowX='scroll')
            ),
            width=12, align='left'
        )
    ]),

    html.Br(), html.Br(),
    # dcc.Graph(id='daily_expiryDayRetrnsDistributinChart',  style={'overflow-x': 'scroll', 'height': '90vh'}),
    # html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
],
    style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)

@app.callback(
    [
        Output(component_id='daily_expiryDatatable', component_property='data'),
        Output(component_id='daily_expiryDayReturnsDistributionDatatable', component_property='data'),
    ],
    [
        Input('daily_expirySymbolNameToPlot', 'value'), Input('daily_expiryDateRange', 'start_date'), 
        Input('daily_expiryDateRange', 'end_date'), Input('daily_expiryDayType', 'value'),
        Input('daily_expiryDay', 'value'), Input('daily_expiryReturnPercentageBasis', 'value'), 
        Input('daily_expiryReturnPercentageRange', 'value'), Input('daily_expiryReturnPercentageMonth', 'value'), 
        Input('daily_expiryReturnsDistributionInterval', 'value')
    ]
)
def displayExpiryDayReturns(
    symbolNameToPlotValue, startDate, 
    endDate,expiryDayType, 
    expiryDay,expiryReturnPercentageBasis, 
    expiryReturnPercentageRange, expiryReturnPercentageMonth, 
    expiryReturnsDistributionInterval,
):
    # Read Symbol File, format date and filter vis-a-vis Date Parameters
    try:
        symboldf = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/1_Daily.csv')
        symboldf['Date'] = pd.to_datetime(symboldf['Date'], format='%Y-%m-%d')
        symboldf['ExpiryWeeklyDate'] = pd.to_datetime(symboldf['ExpiryWeeklyDate'], format='%Y-%m-%d')
        symboldf['MondayWeeklyDate'] = pd.to_datetime(symboldf['MondayWeeklyDate'], format='%Y-%m-%d')
        symboldf = symboldf.dropna()
        symboldf = symboldf[(symboldf['Date'] >= startDate) & (symboldf['Date'] <= endDate)].reset_index(drop=True)
    except:
        print(f"Error in fetching {symbolNameToPlotValue} data file")
        print()
    
    latestExpiryChangeDateDict = {'BANKNIFTY': date(2023,9,4),   
                                  'FINNIFTY': date(2021,10,21),
                                  'NIFTY':date(2019,2,13),                   
                                  'SENSEX':date(2023,5,25),                  
                                  'BANKEX':date(2023,5,25),                  
                                  'MIDCPNIFTY': date(2023,8,16)}
    
    oldExpiryWeekdayDict = {'BANKNIFTY': 3, 'FINNIFTY':3, 'MIDCPNIFTY':1 }
    newExpiryWeekdayDict = {'BANKNIFTY': 2, 'FINNIFTY':1, 'MIDCPNIFTY':0}
    sameExpiryWeekdayDict = {'NIFTY': 3, 'BANKEX':0, 'SENSEX':4}    
    
    # expiryDayDistributionChart = go.Figure()
    expiryDayReturnsDataTable = pd.DataFrame()      
    expiryDayDistributionDataTable = pd.DataFrame()
    global expiryDatatableToDownload     
    global expiryDistributionDatatableToDownload
    expiryDayReturnsDataTableToPlot = expiryDayReturnsDataTable.to_dict('records')
    expiryDayDistributionDataTableToPlot = expiryDayDistributionDataTable.to_dict('records')

    returndf = pd.DataFrame()
    
    if(len(symboldf)>0):
        if( (symbolNameToPlotValue in ['BANKNIFTY','FINNIFTY','MIDCPNIFTY']) and expiryDayType==1):
            symboldf = symboldf[ (symboldf['Date'] >= pd.to_datetime(latestExpiryChangeDateDict[symbolNameToPlotValue], format='%Y-%m-%d'))
                                ].reset_index(drop=True)
        elif(symbolNameToPlotValue in ['SENSEX', 'BANKEX', 'NIFTY']):
            symboldf = symboldf[ (symboldf['Date'] >= pd.to_datetime(latestExpiryChangeDateDict[symbolNameToPlotValue], format='%Y-%m-%d'))
                                ].reset_index(drop=True)
        
        if(expiryReturnPercentageMonth!='All'):
            symboldf = symboldf[symboldf['Date'].dt.strftime('%b')==expiryReturnPercentageMonth]
        
        if(len(symboldf)>0):    
            df = symboldf.copy(deep=True)
            getDates = symboldf['Date'].unique()
            symboldf = symboldf.set_index('Date')
            expiryReturnsDict = dict()
            
            for dates in getDates:
                # print(dates)
                dates = pd.to_datetime(dates, format='%Y-%m-%d')
                filter_date1 = dates - timedelta(days=1) if (expiryReturnPercentageBasis==0) else dates
                filter_date2 = dates
                data = pd.DataFrame()
                filtered_df = df[df['Date']>=filter_date2].reset_index(drop=True)

                if( (dates>=pd.to_datetime(latestExpiryChangeDateDict[symbolNameToPlotValue], format='%Y-%m-%d'))
                    and (symbolNameToPlotValue in ['BANKNIFTY','FINNIFTY','MIDCPNIFTY'])
                ):
                    if( ((int(symboldf.loc[dates]['ExpiryWeekNumberMonthly'])==4) and ((expiryDay==0) or (expiryDay==3)) )
                        and (symbolNameToPlotValue=='BANKNIFTY')
                        and (dates < pd.to_datetime(date(2024,3,1), format='%Y-%m-%d'))
                    ):
                        if( (dates.weekday()==3)
                            and (filtered_df.loc[0]['Date'].weekday()==3)
                            and (dates < pd.to_datetime(date(2024,3,1), format='%Y-%m-%d'))
                        ):              
                            data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                        elif( (dates.weekday()<3) 
                            and (filtered_df.loc[0]['Date'].weekday()>3)
                        ):              
                            data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                        elif( (dates.weekday()<3)
                            and (filtered_df.loc[0]['Date'].weekday()<3)
                            and (filtered_df.loc[0]['Date'].weekday()<dates.weekday())
                        ):
                            data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]

                    elif( dates.weekday()==newExpiryWeekdayDict[symbolNameToPlotValue]
                          and ((expiryDay==0) or (expiryDay==2 and symbolNameToPlotValue in ['BANKNIFTY']))
                        ):
                         data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                
                    elif( (dates.weekday()<newExpiryWeekdayDict[symbolNameToPlotValue]) 
                        and ((expiryDay==0) or (expiryDay==2 and symbolNameToPlotValue in ['BANKNIFTY']))
                        and (filtered_df.loc[0]['Date'].weekday()>newExpiryWeekdayDict[symbolNameToPlotValue])
                    ): 
                        data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                    elif( (dates.weekday()<newExpiryWeekdayDict[symbolNameToPlotValue])
                            and ((expiryDay==0) or (expiryDay==2 and symbolNameToPlotValue in ['BANKNIFTY']))
                            and (filtered_df.loc[0]['Date'].weekday()<newExpiryWeekdayDict[symbolNameToPlotValue])
                            and (filtered_df.loc[0]['Date'].weekday()<dates.weekday())
                    ):
                        data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                    elif( (dates.weekday()>newExpiryWeekdayDict[symbolNameToPlotValue])
                        and (filtered_df.loc[0]['Date'].weekday()>newExpiryWeekdayDict[symbolNameToPlotValue])
                        and (filtered_df.loc[0]['Date'].weekday() < dates.weekday())
                        and ((expiryDay==0) or (expiryDay==2 and symbolNameToPlotValue in ['BANKNIFTY']))
                    ):
                        data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                                                
                else:
                    if(symbolNameToPlotValue in oldExpiryWeekdayDict.keys()):
                        if (dates.weekday()== oldExpiryWeekdayDict[symbolNameToPlotValue]):
                            data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                        elif( (dates.weekday()<oldExpiryWeekdayDict[symbolNameToPlotValue]) 
                            and (filtered_df.loc[0]['Date'].weekday()>oldExpiryWeekdayDict[symbolNameToPlotValue])
                        ): 
                            data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                        elif( (dates.weekday()<oldExpiryWeekdayDict[symbolNameToPlotValue])
                                and (filtered_df.loc[0]['Date'].weekday()<oldExpiryWeekdayDict[symbolNameToPlotValue])
                                and (filtered_df.loc[0]['Date'].weekday()<dates.weekday())
                        ):
                            data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                        elif( (dates.weekday()>oldExpiryWeekdayDict[symbolNameToPlotValue])
                            and (filtered_df.loc[0]['Date'].weekday()>oldExpiryWeekdayDict[symbolNameToPlotValue])
                            and (filtered_df.loc[0]['Date'].weekday() < dates.weekday())
                        ):
                            data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]  

                    elif(symbolNameToPlotValue in sameExpiryWeekdayDict.keys()):
                        if(dates.weekday()== sameExpiryWeekdayDict[symbolNameToPlotValue]):
                            data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                        elif( (dates.weekday()<sameExpiryWeekdayDict[symbolNameToPlotValue]) 
                            and (filtered_df.loc[0]['Date'].weekday()>sameExpiryWeekdayDict[symbolNameToPlotValue])
                        ): 
                            data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                        elif( (dates.weekday()<sameExpiryWeekdayDict[symbolNameToPlotValue])
                                and (filtered_df.loc[0]['Date'].weekday()<sameExpiryWeekdayDict[symbolNameToPlotValue])
                                and (filtered_df.loc[0]['Date'].weekday()<dates.weekday())
                        ):
                            data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                        elif( (dates.weekday()>sameExpiryWeekdayDict[symbolNameToPlotValue])
                            and (filtered_df.loc[0]['Date'].weekday()>sameExpiryWeekdayDict[symbolNameToPlotValue])
                            and (filtered_df.loc[0]['Date'].weekday() < dates.weekday())
                        ):
                            data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]  
                
                if(len(data)>0):
                    data = data.reset_index(drop=True)
                    threshold_date = dates - timedelta(days=7)
                    if(expiryReturnPercentageBasis==0):
                        if(len(data)==1):
                            while(len(data)==1 and filter_date1>threshold_date):
                                filter_date1 = filter_date1 - timedelta(days=1)
                                data = df[(df['Date']>=filter_date1) & (df['Date']<=filter_date2)]
                            data = data.reset_index(drop=True)
                        if(len(data)>1):
                            startValue = data.loc[0]['Close']
                            endValue = data.loc[1]['Close']
                        percentageReturn = round(((endValue-startValue)/startValue)*100,2) if len(data)==2 else np.NaN

                    elif(expiryReturnPercentageBasis==1):
                        startValue = data.loc[0]['Open']
                        endValue = data.loc[0]['Close']
                        percentageReturn = round(((endValue-startValue)/startValue)*100,2)

                    elif(expiryReturnPercentageBasis==2):
                        startValue = data.loc[0]['Low']
                        endValue = data.loc[0]['High']
                        percentageReturn = round(((endValue-startValue)/startValue)*100,2)
                    
                    if(percentageReturn!=np.NaN):    
                        expiryReturnsDict[dates] = [percentageReturn, int(data.loc[0]['ExpiryWeekNumberMonthly'])]
            
            if (len(expiryReturnsDict) > 0):
                expiry_returns_list = []
                for dates, values in expiryReturnsDict.items():
                    return_percentage, expiry_week_number = values
                    expiry_returns_list.append({'Date': dates, 'Month': dates.strftime('%b'), 'ReturnPercentage': return_percentage, 'ExpiryWeekNumber': expiry_week_number})
                returndf = pd.DataFrame(expiry_returns_list) 
                if(expiryDay!=-1):
                    returndf = returndf[(pd.to_datetime(returndf['Date'], format='%Y-%m-%d').dt.weekday==expiryDay)]
                
                # Pivot table and reset index
                if(len(returndf)>0):
                    expiryDayReturnsDataTable = returndf.pivot_table(index='Month', columns='ExpiryWeekNumber', values='ReturnPercentage', aggfunc='mean')
                    expiryDayReturnsDataTable = expiryDayReturnsDataTable.reset_index().round(2)
                    cols = expiryDayReturnsDataTable.columns.tolist()
                    cols = ['Month'] + [col for col in cols if col != 'Month']
                    expiryDayReturnsDataTable = expiryDayReturnsDataTable[cols]
                    #Apply Range if both points are not 0
                    if(expiryReturnPercentageRange[0]!=expiryReturnPercentageRange[1]):
                        expiryDayReturnsDataTable.iloc[:, 1:6] = expiryDayReturnsDataTable.iloc[:, 1:6].applymap(lambda x: x if (x >= expiryReturnPercentageRange[0] and 
                                                                                                                          x <= expiryReturnPercentageRange[1])
                                                                                              else np.nan)
                    minReturn = returndf['ReturnPercentage'].min()
                    maxReturn = returndf['ReturnPercentage'].max()
                    frequencyDetails = dict()
                    frequencyList = list()
                    while minReturn <= maxReturn:
                        upper_bound = round(minReturn + expiryReturnsDistributionInterval, 2)
                        frequencyDetails[f'{round(minReturn, 2)} - {upper_bound}'] = len(returndf[
                                            (returndf['ReturnPercentage'] >= round(minReturn, 2)) 
                                            & (returndf['ReturnPercentage'] < upper_bound)
                                            ]) 
                        minReturn = round(minReturn + expiryReturnsDistributionInterval,2)
                    for interval, value in frequencyDetails.items():
                        frequencyList.append({'Interval': interval, 'Frequency': value})
                    if(len(frequencyList)>0):
                        expiryDayDistributionDataTable = pd.DataFrame(frequencyList)
                        expiryDayDistributionDataTableToPlot = expiryDayDistributionDataTable.to_dict('records')

            
    if(len(expiryDayReturnsDataTable)>0):
        expiryDayReturnsDataTableToPlot = expiryDayReturnsDataTable.to_dict('records')
    
    return [expiryDayReturnsDataTableToPlot, expiryDayDistributionDataTableToPlot]

if __name__ == '__main__':
    app.run_server(debug=True)
