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
from helper import symbolNamesToDropdown, watchListToDropDown, specialDaysToDropdown, monthFullNames, \
    weekDays, tradingDays, calenderDays, colorDict, \
    getDataTableForPlot, getDataTableStatistics, getMonthNumber


electionDatatableToDownload = pd.DataFrame()
electionCumulativeReturnsDatatableToDownload = pd.DataFrame()
midElectionDatatableToDownload = pd.DataFrame()
electionMonthlyDatatableToDownload = pd.DataFrame()
electionMonthlyCumulativeReturnsDatatableToDownload = pd.DataFrame()
exitPollReturnsDatatableToDownload = pd.DataFrame()


dailyTimeFrameElectionLayout =  html.Div([
    html.Br(), html.Br(),

    # Election Year Inputs
    html.H2('Election Year Inputs'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Election State'), width=4, align='left'),
        dbc.Col(html.H6('Select Symbol'), width=4, align='left'),
         dbc.Col(html.H6('Select Date Range'), width=4, align='left'),
        
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_electionState',
                           inline=True,
                           options=[dict(label='USA', value='USA'),
                                    dict(label='INDIA', value='INDIA')],
                           value='INDIA',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_electionSymbolNameToPlot',
                                   options=symbolNamesToDropdown,
                                   value='BANKNIFTY',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='50%')),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.DatePickerRange(id='daily_electionDateRange',
                                min_date_allowed=date(1900, 1, 1), max_date_allowed=date(2025, 12, 31),
                                start_date=date(2016, 1, 1), end_date=date(2023, 12, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Time Range'), width=4, align='left'),
        dbc.Col(html.H6('Select Time Range Type'), width=4, align='left'),
        dbc.Col(html.H6('Enter Time Range Value'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_electionRangeType',
                           inline=True,
                           options=[dict(label='Pre', value='Pre'),
                                    dict(label='Post', value='Post'),
                                    dict(label='Both', value='Both')
                           ],
                           value='Pre',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_electionTimeRangeType',
                        inline=True,
                        options=[dict(label='Days', value='Days'),
                                dict(label='Weeks', value='Weeks'),
                                dict(label='Months', value='Months')
                                ],
                        value='Days',
                        className='radiobutton-group',
                        persistence=True, persistence_type='session'),
        width=4, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='daily_electionTimeRangeValue',
                                type='number',
                                placeholder='Enter the maximum time range value',
                                style={'width': '250px', 'height': '30px'},
                                min=1, step=1, value=10, 
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=4, align='left'
        ),
    ]),
    
    html.Br(),
    html.Hr(),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Week Range Sub-Type'), width=4, align='left'),
        dbc.Col(html.H6('Select Month Range Sub-Type'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_electionWeekSubType',
                        inline=True,
                        options=[dict(label='Friday-To-Friday', value=0),
                                dict(label='Weekly', value=1),
                                ],
                        value=0,
                        className='radiobutton-group',
                        persistence=True, persistence_type='session'),
        width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_electionMonthSubType',
                        inline=True,
                        options=[dict(label='Day-To-Day', value=0),
                                dict(label='Monthly', value=1),
                                ],
                        value=0,
                        className='radiobutton-group',
                        persistence=True, persistence_type='session'),
        width=4, align='left'
        ),
    ]),
    html.Br(),

    dbc.Row([
         dbc.Col(html.H6('Month Outliers'), width=4, align='left'),
         dbc.Col(html.H6('Select Superimposed Value to Plot'), width=4, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_electionMonthOutlierToggle',
                        inline=True,
                        options=[dict(label='Include', value=0),
                                dict(label='Exclude', value=1),
                                ],
                        value=1,
                        className='radiobutton-group',
                        persistence=True, persistence_type='session'),
        width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_electionSuperimposedChartValue',
                           inline=True,
                           options=[dict(label='Average', value='Average'),
                                    dict(label='Sum', value='Sum')],
                           value='Average',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),

    ]),
    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.Br(), 
    
    # Election Year Output
    html.H2('Election Year Output'),
    html.Br(),
    html.H4("Individual Returns"),
    html.Br(),
    dbc.Button(id='daily_electionDatatable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
    ),
    dcc.Download(id='daily_electionDatatable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([
                dash_table.DataTable(id='daily_electionDatatable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=
                                            [
                                               {
                                               'if': {
                                                   'column_id': 'Election Date',
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
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.Br(),
    html.H4("Cumulative Returns"),
    html.Br(),
    dbc.Button(id='daily_electionCumulativeReturnsDatatable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
    ),
    dcc.Download(id='daily_electionCumulativeReturnsDatatable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([
                dash_table.DataTable(id='daily_electionCumulativeReturnsDatatable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=
                                            [
                                               {
                                               'if': {
                                                   'column_id': 'Election Date',
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
    html.H4('Election Year Superimposed Chart'),
    html.Br(),
    dcc.Graph(id='daily_electionSuperimposedChart',  style={'overflow-x': 'scroll', 'height': '90vh'}),
    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    
    # Election Date and Exit Poll Returns
    html.Br(),
    html.H2('Exit Poll Returns'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Value'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_exitPollReturnsValueBasis',
                           inline=True,
                           options=[dict(label='Open-To-Close', value=0),
                                    dict(label='Close-To-Close', value=1),
                           ],
                           value=0,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
    ]),
    html.Br(),
    dbc.Button(id='daily_exitPollReturnsDatatable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
    ),
    dcc.Download(id='daily_exitPollReturnsDatatable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([
                dash_table.DataTable(id='daily_exitPollReturnsDatatable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=
                                            [
                                               {
                                               'if': {
                                                   'column_id': 'Election Date',
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
            width=6, align='left'
        )
    ]),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    
    # Mid-Election
    html.Br(), 
    html.H2('Mid-Election Year Inputs'),
    html.Br(),
    
    dbc.Row([
        dbc.Col(html.H6('Select Mid-Election Year Type'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_electionMidYearTrendType',
                           inline=True,
                           options=[dict(label='Bear', value='Bear'),
                                    dict(label='Any', value='Any'),
                           ],
                           value='Any',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    html.Br(),
    html.H2('Mid-Election Year Output'),
    html.Br(),
    dbc.Button(id='daily_midElectionDatatable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
    ),
    dcc.Download(id='daily_midElectionDatatable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_midElectionDatatable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[
                                               {
                                               'if': {
                                                   'column_id': 'index',
                                               },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold'
                                                },
                                            ],
                                           style_cell=dict(
                                               whiteSpace='pre-line',
                                               textAlign= 'center',
                                           ),
                                           style_header=dict(
                                               width='8px', minWidth='8px', maxWidth='8px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold',
                                               textAlign= 'center',
                                           ),
                                           style_data=dict(
                                               width='8px', minWidth='8px', maxWidth='8px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='white', color='black',
                                               textAlign= 'center',
                                           )),],
                     style=dict(width='100%')),
            width=4, align='left'
        )
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
],
    style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)


@callback(
    [
        Output(component_id='daily_electionDatatable', component_property='data'),
        Output(component_id='daily_electionCumulativeReturnsDatatable', component_property='data'),
        Output(component_id='daily_electionSuperimposedChart', component_property='figure'),
    ],
    [
        Input('daily_electionState', 'value'), Input('daily_electionSymbolNameToPlot', 'value'),
        Input('daily_electionDateRange', 'start_date'), Input('daily_electionDateRange', 'end_date'), 
        Input('daily_electionRangeType', 'value'), Input('daily_electionTimeRangeType', 'value'), 
        Input('daily_electionTimeRangeValue', 'value'), Input('daily_electionMonthOutlierToggle', 'value'),
        Input('daily_electionWeekSubType', 'value'),Input('daily_electionMonthSubType', 'value'), 
        Input('daily_electionSuperimposedChartValue', 'value'),
    ]
)
def displayElectionReturns(
    electionState, symbolNameToPlotValue, 
    startDate, endDate,
    electionRangeType, electionTimeRangeType,
    electionTimeRangeValue, electionMonthOutlierToggle,
    electionWeekSubType, electionMonthSubType,
    electionSuperImposedChartValue,
):
    # Read Symbol File
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
    
    for column in symboldf.columns:
        if symboldf[column].dtype == 'object' and all(symboldf[column].astype(str).str.lower().isin(['true', 'false'])):
            symboldf[column] = symboldf[column].astype(bool)
    
    # Read Election Dates File
    try:
        electionDates = pd.read_csv('./elections/' + electionState + '.csv')
        electionDates = electionDates['Date'].dropna()
        electionDates = pd.to_datetime(electionDates, format='%Y-%m-%d')
        electionDates = electionDates[(electionDates>=symboldf['Date'].min())
                                      & (electionDates<=symboldf['Date'].max())
                        ].reset_index(drop=True)
        # May for India and November for USA as normalized Election Months
        if(electionMonthOutlierToggle==1 and electionState=='INDIA'):
            electionDates = electionDates[pd.to_datetime(electionDates, format='%Y-%m-%d').dt.month == 5]
        elif(electionMonthOutlierToggle==1 and electionState=='USA'):
            electionDates = electionDates[pd.to_datetime(electionDates, format='%Y-%m-%d').dt.month ==11]
    except:
        print(f"Error in fetching {electionState} data file")
        print()
    
    electionDates = electionDates.to_list()
    
    # To address run time error when user deletes the value from Input component
    if(electionTimeRangeValue==None):
        electionTimeRangeValue = 10
    
    # Columns Order for Individual datatable to Plot
    returnColumns = list()
    lengthCheck = 1  # For Date
    
    if(electionRangeType=='Pre'):
        if(electionTimeRangeType=='Days'):
            returnColumns = ['T-' + str(i)  for i in range(electionTimeRangeValue-1, 0, -1)]
        else:
            returnColumns = ['T-' + str(i)  for i in range(electionTimeRangeValue, 0, -1)]
        
        if(electionTimeRangeType=='Days' 
           or (electionTimeRangeType=="Months" and electionMonthSubType==1)
        ):
            returnColumns.append('T')
    elif(electionRangeType=='Post'):
        if(electionTimeRangeType=='Days' 
           or (electionTimeRangeType=="Months" and electionMonthSubType==1)
        ):
            returnColumns.append('T')
        returnColumns = returnColumns + ['T+' + str(i)  for i in range(1, electionTimeRangeValue+1, 1)]
    else:
        if(electionTimeRangeType=='Days'):
            returnColumns = ['T-' + str(i)  for i in range(electionTimeRangeValue-1, 0, -1)]
        else:
            returnColumns = ['T-' + str(i)  for i in range(electionTimeRangeValue, 0, -1)]
        
        if(electionTimeRangeType=='Days' 
           or (electionTimeRangeType=="Months" and electionMonthSubType==1)
        ):
            returnColumns.append('T')
        returnColumns = returnColumns + ['T+' + str(i)  for i in range(1, electionTimeRangeValue+1, 1)]

    lengthCheck = lengthCheck + len(returnColumns) 
    #Datatables and Figures Declaration
    electionReturnsDatatable = pd.DataFrame(columns=['Election Date', *returnColumns])
    electionReturnsDatatableToPlot = electionReturnsDatatable.to_dict('records')
    
    cumulativeReturnsDatatable = pd.DataFrame()
    cumulativeReturnsDatatableToPlot = cumulativeReturnsDatatable.to_dict('records')
    
    electionReturnsDatatableForFigure = pd.DataFrame()
    electionReturnsFigure = go.Figure()
    count = -1
    
    #Main 
    for electionDate in electionDates: 
        electionDate = pd.to_datetime(electionDate, format='%Y-%m-%d')
        electionDateIndex = None
        returnsFromDate = None
        returnsToDate = None
        electionDateDf = pd.DataFrame()
        returnsFiltered_df = pd.DataFrame() 
          
        if(electionTimeRangeType=='Days'):  
            electionDateDf = symboldf[symboldf['Date']==electionDate] 
            if(len(electionDateDf)>0):
                electionDateIndex =  electionDateDf.index.values[0]          
            else:
                print(f"{pd.to_datetime(electionDate, format='%Y-%m-%d').strftime('%d-%m-%Y')} is a trading holiday")
                tempDate = electionDate
                tempDate = pd.to_datetime(tempDate, format='%Y-%m-%d')          
                while(tempDate not in symboldf['Date'].values):  #Shifts to next available Date in case the election Date is a holiday
                    tempDate = tempDate + pd.DateOffset(days=1)
                    tempDate = pd.to_datetime(tempDate, format='%Y-%m-%d')    
                print("The next available Date for Returns on T Day is ", tempDate.strftime('%d-%m-%Y'))
                print()
                electionDateDf = symboldf[symboldf['Date']==tempDate] 
                electionDateIndex = electionDateDf.index.values[0] 

            if(electionRangeType=='Pre' 
                and electionDateIndex!=None 
                and electionDateIndex >= electionTimeRangeValue
            ):   
                returnsFiltered_df = symboldf[electionDateIndex-electionTimeRangeValue+1:electionDateIndex+1].reset_index(drop=True)
            elif(electionRangeType=='Post' 
                and electionDateIndex!=None 
                and electionDateIndex >= 0
                and (len(symboldf) >= electionDateIndex+electionTimeRangeValue)
            ):  
                returnsFiltered_df = symboldf[electionDateIndex:electionDateIndex+electionTimeRangeValue+1].reset_index(drop=True)  
            elif(electionRangeType=='Both'
                and electionDateIndex!=None 
                and electionDateIndex >= electionTimeRangeValue
                and (len(symboldf) >= electionDateIndex+electionTimeRangeValue)
            ):  
                returnsFiltered_df = symboldf[electionDateIndex-electionTimeRangeValue+1:electionDateIndex+electionTimeRangeValue+1].reset_index(drop=True)      
            
            if(len(returnsFiltered_df)>0):
                returnsFiltered_df = returnsFiltered_df.groupby('Date', sort=False)
            else:
                if(electionDateIndex < electionTimeRangeValue):
                    print(f"Data insufficient for {electionRangeType} selection query on {pd.to_datetime(electionDate, format='%Y-%m-%d').strftime('%d-%m-%Y')} (Reason - {electionDateIndex} < {electionTimeRangeValue})")
                    print()
                else:
                    print(f"Data insufficient for {electionRangeType} selection query on {pd.to_datetime(electionDate, format='%Y-%m-%d').strftime('%d-%m-%Y')} (Reason - {electionDateIndex} > {electionTimeRangeValue})")
                    print()
        
        elif(electionTimeRangeType=='Weeks'):        
            returnsFinal_df = pd.DataFrame()

            if(electionRangeType=='Pre'):
                returnsFromDate = electionDate    
                
                # if user selects Friday to Friday, then date shifted to Friday else fromDate will be electionDate
                if(electionWeekSubType==0):
                    if(returnsFromDate.weekday()<4):
                        returnsFromDate = returnsFromDate + timedelta(days=(4-returnsFromDate.weekday()))
                    elif(returnsFromDate.weekday()>4):
                        returnsFromDate = returnsFromDate - timedelta(days=(returnsFromDate.weekday()-4))  
                # If Friday-To-Friday -> shift one week backward
                # If Weekly- T-1 - > if Day is M/T get Previous to Previous week's friday 
                # else previous week's Friday
                if(electionWeekSubType==0):
                    returnsToDate = returnsFromDate - pd.DateOffset(weeks=1)
                elif(electionWeekSubType==1):
                    if(returnsFromDate.weekday() in [0, 1]):
                        returnsToDate = returnsFromDate - pd.DateOffset(weeks=2)
                    else:
                        returnsToDate = returnsFromDate - pd.DateOffset(weeks=1)
                    # Since shift is from ElectionDate, returnsToDate has to be a Friday
                    if(returnsToDate.weekday() > 4):
                        returnsToDate = returnsToDate - timedelta(days=returnsToDate.weekday()-4)
                    elif(returnsToDate.weekday() < 4):
                        returnsToDate = returnsToDate + timedelta(days= 4-returnsToDate.weekday()) 
                
                # If ElectionDate is a weekend and subtype is 'Weekly'- get Monday Data
                if(returnsFromDate.weekday()>4 and electionWeekSubType==1):
                    returnsFromDate = returnsFromDate + timedelta(days=(7-returnsFromDate.weekday()))
                    # Check if Monday data is available
                    if(returnsFromDate not in symboldf['Date'].values):
                        while(returnsFromDate not in symboldf['Date'].values):
                            returnsFromDate = returnsFromDate + timedelta(days=1)
                
                flag = -1

                for i in range(electionTimeRangeValue): 
                    tempFromDate = returnsFromDate
                    tempToDate = returnsToDate
                    
                    # If Previous Friday Candle is missing; get Thursday Candle - toDate is previous week
                    if(tempToDate not in symboldf['Date'].values):
                        while(tempToDate not in symboldf['Date'].values):
                            tempToDate = tempToDate - pd.DateOffset(days=1)
            
                    returnsFiltered_df = symboldf[ (symboldf['Date'] <= tempFromDate)
                                    & (symboldf['Date'] >= tempToDate)
                                    ].reset_index(drop=True)
                   
                    if(len(returnsFiltered_df)>0):
                        startClose = returnsFiltered_df.loc[0]['Close']
                        endClose = returnsFiltered_df.loc[len(returnsFiltered_df)-1]['Close']
                        value = ((endClose - startClose)/startClose)*100
                        value = round(value, 2)
                        returnsFiltered_df['ElectionWeekReturnPercentage'] = [value]*len(returnsFiltered_df)
                        returnsFiltered_df['WeekFlag'] = [flag]*len(returnsFiltered_df)
                        returnsFinal_df = pd.concat([returnsFiltered_df, returnsFinal_df])
                    
                    returnsFromDate = returnsToDate
                    returnsToDate = returnsToDate - pd.DateOffset(weeks=1)
                    flag = flag - 1
                    # print(returnsFiltered_df[['Date', 'WeekFlag']])
            elif(electionRangeType=='Post'):
                
                returnsFromDate = electionDate 
                if(electionWeekSubType==0):
                    if(returnsFromDate.weekday()<4):
                        returnsFromDate = returnsFromDate + timedelta(days=(4-returnsFromDate.weekday()))
                    elif(returnsFromDate.weekday()>4):
                        returnsFromDate = returnsFromDate - timedelta(days=(returnsFromDate.weekday()-4))
                    returnsToDate = returnsFromDate + pd.DateOffset(weeks=1) 

                elif(electionWeekSubType==1):
                    if((returnsFromDate.weekday() not in [0,1])):
                        returnsToDate = returnsFromDate + pd.DateOffset(weeks=1)
                    else:
                        returnsToDate = returnsFromDate + pd.DateOffset(days=(4-returnsFromDate.weekday()))

                if(returnsToDate.weekday() > 4):
                    returnsToDate = returnsToDate - timedelta(days=returnsToDate.weekday()-4)
                elif(returnsToDate.weekday() < 4):
                    returnsToDate = returnsToDate + timedelta(days= 4-returnsToDate.weekday()) 
                
                flag = 1 
                
                for i in range(electionTimeRangeValue): 
                    tempFromDate = returnsFromDate      #Here fromDate is current week and toDate is next Week
                    tempToDate = returnsToDate   
                    returnsFiltered_df = symboldf[ (symboldf['Date'] >= tempFromDate)
                                    & (symboldf['Date'] <= tempToDate)
                                    ].reset_index(drop=True)
                    startClose = returnsFiltered_df.loc[0]['Close']
                    endClose = returnsFiltered_df.loc[len(returnsFiltered_df)-1]['Close']
                    value = ((endClose - startClose)/startClose)*100
                    value = round(value, 2)
                    returnsFiltered_df['ElectionWeekReturnPercentage'] = [value]*len(returnsFiltered_df)
                    returnsFiltered_df['WeekFlag'] = [flag]*len(returnsFiltered_df)
                    returnsFinal_df = pd.concat([returnsFinal_df, returnsFiltered_df])
                    returnsFromDate = returnsToDate
                    returnsToDate = returnsToDate + pd.DateOffset(weeks=1)
                    flag = flag + 1
            
            else:
                # Pre Logic
                returnsFromDate = electionDate    
                
                # if user selects Friday to Friday, then date shifted to Friday else fromDate will be electionDate
                if(electionWeekSubType==0):
                    if(returnsFromDate.weekday()<4):
                        returnsFromDate = returnsFromDate + timedelta(days=(4-returnsFromDate.weekday()))
                    elif(returnsFromDate.weekday()>4):
                        returnsFromDate = returnsFromDate - timedelta(days=(returnsFromDate.weekday()-4))  
                # If Friday-To-Friday -> shift one week backward
                # If Weekly- T-1 - > if Day is M/T get Previous to Previous week's friday 
                # else previous week's Friday
                if(electionWeekSubType==0):
                    returnsToDate = returnsFromDate - pd.DateOffset(weeks=1)
                elif(electionWeekSubType==1):
                    if(returnsFromDate.weekday() in [0, 1]):
                        returnsToDate = returnsFromDate - pd.DateOffset(weeks=2)
                    else:
                        returnsToDate = returnsFromDate - pd.DateOffset(weeks=1)
                    # Since shift is from ElectionDate, returnsToDate has to be a Friday
                    if(returnsToDate.weekday() > 4):
                        returnsToDate = returnsToDate - timedelta(days=returnsToDate.weekday()-4)
                    elif(returnsToDate.weekday() < 4):
                        returnsToDate = returnsToDate + timedelta(days= 4-returnsToDate.weekday()) 
                
                # If ElectionDate is a weekend and subtype is 'Weekly'- get Monday Data
                if(returnsFromDate.weekday()>4 and electionWeekSubType==1):
                    returnsFromDate = returnsFromDate + timedelta(days=(7-returnsFromDate.weekday()))
                    # Check if Monday data is available
                    if(returnsFromDate not in symboldf['Date'].values):
                        while(returnsFromDate not in symboldf['Date'].values):
                            returnsFromDate = returnsFromDate + timedelta(days=1)
                
                flag = -1

                for i in range(electionTimeRangeValue): 
                    tempFromDate = returnsFromDate
                    tempToDate = returnsToDate
                    
                    # If Previous Friday Candle is missing; get Thursday Candle - toDate is previous week
                    if(tempToDate not in symboldf['Date'].values):
                        while(tempToDate not in symboldf['Date'].values):
                            tempToDate = tempToDate - pd.DateOffset(days=1)
            
                    returnsFiltered_df = symboldf[ (symboldf['Date'] <= tempFromDate)
                                    & (symboldf['Date'] >= tempToDate)
                                    ].reset_index(drop=True)
                   
                    if(len(returnsFiltered_df)>0):
                        startClose = returnsFiltered_df.loc[0]['Close']
                        endClose = returnsFiltered_df.loc[len(returnsFiltered_df)-1]['Close']
                        value = ((endClose - startClose)/startClose)*100
                        value = round(value, 2)
                        returnsFiltered_df['ElectionWeekReturnPercentage'] = [value]*len(returnsFiltered_df)
                        returnsFiltered_df['WeekFlag'] = [flag]*len(returnsFiltered_df)
                        returnsFinal_df = pd.concat([returnsFiltered_df, returnsFinal_df])
                    
                    returnsFromDate = returnsToDate
                    returnsToDate = returnsToDate - pd.DateOffset(weeks=1)
                    flag = flag - 1
            
            # Post Logic
                returnsFromDate = electionDate 
                if(electionWeekSubType==0):
                    if(returnsFromDate.weekday()<4):
                        returnsFromDate = returnsFromDate + timedelta(days=(4-returnsFromDate.weekday()))
                    elif(returnsFromDate.weekday()>4):
                        returnsFromDate = returnsFromDate - timedelta(days=(returnsFromDate.weekday()-4))
                    returnsToDate = returnsFromDate + pd.DateOffset(weeks=1) 

                elif(electionWeekSubType==1):
                    if((returnsFromDate.weekday() not in [0,1])):
                        returnsToDate = returnsFromDate + pd.DateOffset(weeks=1)
                    else:
                        returnsToDate = returnsFromDate + pd.DateOffset(days=(4-returnsFromDate.weekday()))

                if(returnsToDate.weekday() > 4):
                    returnsToDate = returnsToDate - timedelta(days=returnsToDate.weekday()-4)
                elif(returnsToDate.weekday() < 4):
                    returnsToDate = returnsToDate + timedelta(days= 4-returnsToDate.weekday()) 
                
                flag = 1 
                
                for i in range(electionTimeRangeValue): 
                    tempFromDate = returnsFromDate      #Here fromDate is current week and toDate is next Week
                    tempToDate = returnsToDate   
                    returnsFiltered_df = symboldf[ (symboldf['Date'] >= tempFromDate)
                                    & (symboldf['Date'] <= tempToDate)
                                    ].reset_index(drop=True)
                    startClose = returnsFiltered_df.loc[0]['Close']
                    endClose = returnsFiltered_df.loc[len(returnsFiltered_df)-1]['Close']
                    value = ((endClose - startClose)/startClose)*100
                    value = round(value, 2)
                    returnsFiltered_df['ElectionWeekReturnPercentage'] = [value]*len(returnsFiltered_df)
                    returnsFiltered_df['WeekFlag'] = [flag]*len(returnsFiltered_df)
                    returnsFinal_df = pd.concat([returnsFinal_df, returnsFiltered_df])
                    returnsFromDate = returnsToDate
                    returnsToDate = returnsToDate + pd.DateOffset(weeks=1)
                    flag = flag + 1
            
            #First sort by WeekFlag so that it matches order of 'ReturnColumns'
            # and Groupby then 
            if(len(returnsFinal_df)>0):
                returnsFinal_df = returnsFinal_df.sort_values(by=['WeekFlag'])   
                returnsFiltered_df = returnsFinal_df.copy(deep=True)
                returnsFiltered_df = returnsFiltered_df.groupby('WeekFlag')

        elif(electionTimeRangeType=='Months'):
            returnsFinal_df = pd.DataFrame()
            tempElectionTimeRangeValue = electionTimeRangeValue 
            if(electionMonthSubType==1):
                tempElectionTimeRangeValue = tempElectionTimeRangeValue + 1

            # Gets back to earliest date -FromDate and increments by 1 month -ToDate
            if(electionRangeType=='Pre'):
                flag = -electionTimeRangeValue                 
                # Gets to n months back
                returnsFromDate = electionDate - pd.DateOffset(months=electionTimeRangeValue)
               
                for i in range(tempElectionTimeRangeValue): 
                    returnsToDate = returnsFromDate + pd.DateOffset(months=1)      
                    if(electionMonthSubType==0):
                        tempFromDate = returnsFromDate
                        tempToDate = returnsToDate
                        if(tempFromDate not in symboldf['Date'].values):
                            while(tempFromDate not in symboldf['Date'].values):
                                tempFromDate = tempFromDate - pd.DateOffset(days=1)
                        if(tempToDate not in symboldf['Date'].values):
                            while(tempToDate not in symboldf['Date'].values):
                                tempToDate = tempToDate + pd.DateOffset(days=1)    

                        returnsFiltered_df = symboldf[ 
                                                (symboldf['Date'] <= tempToDate)
                                                & (symboldf['Date'] >= tempFromDate)
                                        ].reset_index(drop=True)
                        
                        if(len(returnsFiltered_df)>0):
                            returnsFiltered_df['ElectionMonthFlag'] = [flag] * len(returnsFiltered_df)
                            startClose = returnsFiltered_df.loc[0]['Close']
                            endClose = returnsFiltered_df.loc[len(returnsFiltered_df)-1]['Close']
                            value = ((endClose - startClose)/startClose)*100
                            value = round(value, 2)
                            returnsFiltered_df['ElectionMonthReturnPercentage'] = [value] * len(returnsFiltered_df)
                            returnsFinal_df = pd.concat([returnsFinal_df, returnsFiltered_df])
                            # print(returnsFiltered_df[['Date', 'Close', 'ElectionMonthFlag', 'ElectionMonthReturnPercentage']])
                    elif(electionMonthSubType==1):
                        # Gets Current Month Data
                        returnsFiltered_df = symboldf[ (symboldf['Date'].dt.month==returnsFromDate.month)
                                                        & (symboldf['Date'].dt.year==returnsFromDate.year)
                                             ].reset_index(drop=True)   
                        if(len(returnsFiltered_df)>0):
                            returnsFiltered_df['ElectionMonthFlag'] = [flag] * len(returnsFiltered_df)
                            returnsFiltered_df['ElectionMonthReturnPercentage'] = returnsFiltered_df['MonthlyReturnPercentage']
                            returnsFinal_df = pd.concat([returnsFinal_df, returnsFiltered_df])
                            
                    flag = flag + 1
                    returnsFromDate = returnsToDate
                
            elif(electionRangeType=='Post'):  
                flag = 1
                returnsFromDate = electionDate                 
                returnsToDate = returnsFromDate + pd.DateOffset(months=1)
                for i in range(tempElectionTimeRangeValue):   
                    if(electionMonthSubType==0):
                        tempFromDate = returnsFromDate
                        tempToDate = returnsToDate
                        if(tempFromDate not in symboldf['Date'].values):
                            while(tempFromDate not in symboldf['Date'].values):
                                tempFromDate = tempFromDate - pd.DateOffset(days=1)
                        if(tempToDate not in symboldf['Date'].values):
                            while(tempToDate not in symboldf['Date'].values):
                                tempToDate = tempToDate + pd.DateOffset(days=1)      
                        returnsFiltered_df = symboldf[  (symboldf['Date'] <= tempToDate)
                                                        & (symboldf['Date'] >= tempFromDate)
                                                ].sort_values(by='Date').reset_index(drop=True)
                        returnsFiltered_df['ElectionMonthFlag'] = [flag] * len(returnsFiltered_df)
                        startClose = returnsFiltered_df.loc[0]['Close']
                        endClose = returnsFiltered_df.loc[len(returnsFiltered_df)-1]['Close']
                        value = ((endClose-startClose)/startClose)*100
                        value = round(value, 2)
                        returnsFiltered_df['ElectionMonthReturnPercentage'] = [value] * len(returnsFiltered_df)
                        returnsFinal_df = pd.concat([returnsFinal_df, returnsFiltered_df])  
                    
                    elif(electionMonthSubType==1): 
                        returnsFiltered_df = symboldf[ 
                                                        (symboldf['Date'].dt.month==returnsFromDate.month)
                                                        & (symboldf['Date'].dt.year==returnsFromDate.year)
                                             ].reset_index(drop=True)
                        if(len(returnsFiltered_df)>0):
                            returnsFiltered_df['ElectionMonthFlag'] = [flag] * len(returnsFiltered_df)
                            returnsFiltered_df['ElectionMonthReturnPercentage'] = returnsFiltered_df['MonthlyReturnPercentage']
                            returnsFinal_df = pd.concat([returnsFinal_df, returnsFiltered_df])
                    flag = flag + 1
                    returnsFromDate = returnsToDate
                    returnsToDate = returnsToDate + pd.DateOffset(months=1)
                    
            else:
            # Pre Logic
                flag = -electionTimeRangeValue                 
                # Gets to n months back
                returnsFromDate = electionDate - pd.DateOffset(months=electionTimeRangeValue)
                for i in range(tempElectionTimeRangeValue): 
                    returnsToDate = returnsFromDate + pd.DateOffset(months=1)      
                    if(electionMonthSubType==0):
                        tempFromDate = returnsFromDate
                        tempToDate = returnsToDate
                        if(tempFromDate not in symboldf['Date'].values):
                            while(tempFromDate not in symboldf['Date'].values):
                                tempFromDate = tempFromDate - pd.DateOffset(days=1)
                        if(tempToDate not in symboldf['Date'].values):
                            while(tempToDate not in symboldf['Date'].values):
                                tempToDate = tempToDate + pd.DateOffset(days=1)    

                        returnsFiltered_df = symboldf[ 
                                                (symboldf['Date'] <= tempToDate)
                                                & (symboldf['Date'] >= tempFromDate)
                                        ].reset_index(drop=True)
                        
                        if(len(returnsFiltered_df)>0):
                            returnsFiltered_df['ElectionMonthFlag'] = [flag] * len(returnsFiltered_df)
                            startClose = returnsFiltered_df.loc[0]['Close']
                            endClose = returnsFiltered_df.loc[len(returnsFiltered_df)-1]['Close']
                            value = ((endClose - startClose)/startClose)*100
                            value = round(value, 2)
                            returnsFiltered_df['ElectionMonthReturnPercentage'] = [value] * len(returnsFiltered_df)
                            returnsFinal_df = pd.concat([returnsFinal_df, returnsFiltered_df])
                    
                    elif(electionMonthSubType==1):
                        # Gets Current Month Data
                        returnsFiltered_df = symboldf[ (symboldf['Date'].dt.month==returnsFromDate.month)
                                                        & (symboldf['Date'].dt.year==returnsFromDate.year)
                                             ].reset_index(drop=True)   
                        if(len(returnsFiltered_df)>0):
                            returnsFiltered_df['ElectionMonthFlag'] = [flag] * len(returnsFiltered_df)
                            returnsFiltered_df['ElectionMonthReturnPercentage'] = returnsFiltered_df['MonthlyReturnPercentage']
                            returnsFinal_df = pd.concat([returnsFinal_df, returnsFiltered_df])
                    flag = flag + 1
                    returnsFromDate = returnsToDate

            # Post Logic
                flag = 1
                if(electionMonthSubType==0):
                    returnsFromDate = electionDate
                else:    
                    returnsFromDate = electionDate + pd.DateOffset(months=1)   
                
                for i in range(electionTimeRangeValue):   
                    returnsToDate = returnsFromDate + pd.DateOffset(months=1)
                    if(electionMonthSubType==0):
                        tempFromDate = returnsFromDate
                        tempToDate = returnsToDate
                        if(tempFromDate not in symboldf['Date'].values):
                            while(tempFromDate not in symboldf['Date'].values):
                                tempFromDate = tempFromDate - pd.DateOffset(days=1)
                        if(tempToDate not in symboldf['Date'].values):
                            while(tempToDate not in symboldf['Date'].values):
                                tempToDate = tempToDate + pd.DateOffset(days=1)      
                        returnsFiltered_df = symboldf[  (symboldf['Date'] <= tempToDate)
                                                        & (symboldf['Date'] >= tempFromDate)
                                                ].sort_values(by='Date').reset_index(drop=True)
                        returnsFiltered_df['ElectionMonthFlag'] = [flag] * len(returnsFiltered_df)
                        startClose = returnsFiltered_df.loc[0]['Close']
                        endClose = returnsFiltered_df.loc[len(returnsFiltered_df)-1]['Close']
                        value = ((endClose-startClose)/startClose)*100
                        value = round(value, 2)
                        returnsFiltered_df['ElectionMonthReturnPercentage'] = [value] * len(returnsFiltered_df)
                        returnsFinal_df = pd.concat([returnsFinal_df, returnsFiltered_df])  
                    
                    elif(electionMonthSubType==1): 
                        returnsFiltered_df = symboldf[ 
                                                        (symboldf['Date'].dt.month==returnsFromDate.month)
                                                        & (symboldf['Date'].dt.year==returnsFromDate.year)
                                             ].reset_index(drop=True)
                        if(len(returnsFiltered_df)>0):
                            returnsFiltered_df['ElectionMonthFlag'] = [flag] * len(returnsFiltered_df)
                            returnsFiltered_df['ElectionMonthReturnPercentage'] = returnsFiltered_df['MonthlyReturnPercentage']
                            returnsFinal_df = pd.concat([returnsFinal_df, returnsFiltered_df])
                    flag = flag + 1
                    returnsFromDate = returnsToDate
                    
            
            if(len(returnsFinal_df)>0):
                returnsFinal_df = returnsFinal_df.sort_values(by=['ElectionMonthFlag', 'Date'])   
                returnsFiltered_df = returnsFinal_df.copy(deep=True)
                returnsFiltered_df = returnsFiltered_df.groupby('ElectionMonthFlag', sort=False)
                   
        columnValuesList =  list()     
        if(returnsFiltered_df.size):
            columnValuesList.append(electionDate)   #List Info for Datatable as per sequence of Return Columns
            for key, data in returnsFiltered_df:
                data = data.reset_index(drop=True)
                if(electionTimeRangeType=='Days'):
                    returnValue = data.loc[0]['ReturnPercentage']
                elif(electionTimeRangeType=='Weeks'):
                    returnValue = data.loc[0]['ElectionWeekReturnPercentage']
                elif(electionTimeRangeType=='Months'):
                    returnValue = data.loc[0]['ElectionMonthReturnPercentage']
                columnValuesList.append(round(returnValue, 2))
        if(len(columnValuesList)==lengthCheck):
            count = count + 1
            electionReturnsDatatable.loc[count] = columnValuesList      #Column calculations have to match the number of returnColumns
        else:
             print(f"Insufficient Data for election Date {pd.to_datetime(electionDate, format='%Y-%m-%d').strftime('%d-%m-%Y')} on {symbolNameToPlotValue} with {electionTimeRangeValue} {electionTimeRangeType} {electionRangeType} side query")
             print()
             continue
    
    # Cumulative Returns Datatable Calculations
    cumulativeReturnsDatatable = pd.DataFrame(columns=returnColumns)
    cumulativeReturnsDatatable = electionReturnsDatatable[returnColumns].copy(deep=True)
    individualReturns = list()
    cumulativeReturns = list()
    for i in range(0, len(cumulativeReturnsDatatable)):
        individualReturns = electionReturnsDatatable.loc[i][returnColumns].values
        cumulativeReturns = [1] + [individualReturns[j]/100 for j in range(0, len(individualReturns))]
        for j in range(1, len(cumulativeReturns)):
            cumulativeReturns[j] = cumulativeReturns[j-1] + (cumulativeReturns[j-1] *cumulativeReturns[j])  
        for j in range(0, len(cumulativeReturns)):
            cumulativeReturns[j] = round((cumulativeReturns[j]-1)*100, 2)
        cumulativeReturns = cumulativeReturns[1:]
        cumulativeReturnsDatatable.loc[i][returnColumns] = cumulativeReturns  
    
    if(len(cumulativeReturnsDatatable)>0):    
        cumulativeReturnsDatatable['Election Date'] = electionReturnsDatatable['Election Date'].dt.strftime('%d-%m-%Y')
        cumulativeReturnsDatatable = cumulativeReturnsDatatable[[ 'Election Date', *returnColumns]]
        totalCount = [cumulativeReturnsDatatable[colName][cumulativeReturnsDatatable[colName] != 0].count() for colName in returnColumns]
        averageReturns = [round(i, 2) for i in cumulativeReturnsDatatable[returnColumns].mean()]
        totalSum = [round(cumulativeReturnsDatatable[colName][cumulativeReturnsDatatable[colName] != 0].sum(), 2) for colName in returnColumns]

        positiveCount = [cumulativeReturnsDatatable[colName][cumulativeReturnsDatatable[colName] > 0].count() for colName in returnColumns]
        positiveMean = [round(cumulativeReturnsDatatable[colName][cumulativeReturnsDatatable[colName] > 0].mean(), 2) for colName in returnColumns]
        positiveSum = [round(cumulativeReturnsDatatable[colName][cumulativeReturnsDatatable[colName] > 0].sum(), 2) for colName in returnColumns]

        negativeCount = [cumulativeReturnsDatatable[colName][cumulativeReturnsDatatable[colName] < 0].count() for colName in returnColumns]
        negativeMean = [round(cumulativeReturnsDatatable[colName][cumulativeReturnsDatatable[colName] < 0].mean(), 2) for colName in returnColumns]
        negativeSum = [round(cumulativeReturnsDatatable[colName][cumulativeReturnsDatatable[colName] < 0].sum(), 2) for colName in returnColumns]
    
        cumulativeReturnsDatatable = pd.concat([
            cumulativeReturnsDatatable,
            pd.DataFrame({value: [[*['All Count'], *totalCount][i]] for i, value in enumerate(['Election Date', *returnColumns])})
        ])
        cumulativeReturnsDatatable = pd.concat([
            cumulativeReturnsDatatable,
            pd.DataFrame({value: [[*['Pos. Count'], *positiveCount][i]] for i, value in enumerate(['Election Date', *returnColumns])})
        ])
        cumulativeReturnsDatatable = pd.concat([
            cumulativeReturnsDatatable,
            pd.DataFrame({value: [[*['Neg. Count'], *negativeCount][i]] for i, value in enumerate(['Election Date', *returnColumns])})
        ])

        cumulativeReturnsDatatable = pd.concat([
            cumulativeReturnsDatatable,
            pd.DataFrame({value: [[*['Avg Return of All'], *averageReturns][i]] for i, value in enumerate(['Election Date', *returnColumns])})
        ])
        cumulativeReturnsDatatable = pd.concat([
            cumulativeReturnsDatatable,
            pd.DataFrame({value: [[*['Avg Return of Pos.'], *positiveMean][i]] for i, value in enumerate(['Election Date', *returnColumns])})
        ])
        cumulativeReturnsDatatable = pd.concat([
            cumulativeReturnsDatatable,
            pd.DataFrame({value: [[*['Avg Return of Neg.'], *negativeMean][i]] for i, value in enumerate(['Election Date', *returnColumns])})
        ])
        cumulativeReturnsDatatable = pd.concat([
            cumulativeReturnsDatatable,
            pd.DataFrame({value: [[*['Sum Return of All'], *totalSum][i]] for i, value in enumerate(['Election Date', *returnColumns])})
        ])
        cumulativeReturnsDatatable = pd.concat([
            cumulativeReturnsDatatable,
            pd.DataFrame({value: [[*['Sum Return of Pos.'], *positiveSum][i]] for i, value in enumerate(['Election Date', *returnColumns])})
        ])
        cumulativeReturnsDatatable = pd.concat([
            cumulativeReturnsDatatable,
            pd.DataFrame({value: [[*['Sum Return of Neg.'], *negativeSum][i]] for i, value in enumerate(['Election Date', *returnColumns])})
        ])
   
    # Final Datatable to Plot
    if(len(electionReturnsDatatable)>0):
        electionReturnsDatatable['Election Date'] = electionReturnsDatatable['Election Date'].dt.strftime('%d-%m-%Y')
    
    electionReturnsDatatableToPlot = electionReturnsDatatable.to_dict('records')
    global electionDatatableToDownload
    electionDatatableToDownload = dcc.send_data_frame(electionReturnsDatatable.set_index('Election Date').to_csv, f'youngTurtle_electionReturns.csv')
    
    # Figure and its datatable Calculations for Superimposed Returns
    valueDf = pd.DataFrame()
    if(electionSuperImposedChartValue=='Average'):
        valueDf = electionReturnsDatatable[returnColumns].mean() 
    else:
        valueDf = electionReturnsDatatable[returnColumns].sum()  
    individualReturnsAggregate = list()
    cumulativeReturnsAggregate = list()
    if(len(valueDf)>0):
        valueDf = valueDf.reset_index()
        valueDf.columns = ['Date', 'ReturnsAggregate']
        electionReturnsDatatableForFigure = valueDf.copy(deep=True)
        individualReturnsAggregate = electionReturnsDatatableForFigure['ReturnsAggregate'].values
        cumulativeReturnsAggregate = [1] + [individualReturnsAggregate[j]/100 for j in range(0, len(individualReturnsAggregate))]
 
        for j in range(1, len(cumulativeReturnsAggregate)):
            cumulativeReturnsAggregate[j] = cumulativeReturnsAggregate[j-1] + (cumulativeReturnsAggregate[j-1] *cumulativeReturnsAggregate[j]) 
        for j in range(0, len(cumulativeReturnsAggregate)):
            cumulativeReturnsAggregate[j] = round((cumulativeReturnsAggregate[j]-1)*100, 2)
        
        cumulativeReturnsAggregate = cumulativeReturnsAggregate[1:]
        electionReturnsDatatableForFigure['SuperimposedReturn'] = cumulativeReturnsAggregate
        cumulativeReturnsDatatable = pd.concat([
                                        cumulativeReturnsDatatable,
                                        pd.DataFrame({value: [[*['Superimposed Return'], *cumulativeReturnsAggregate][i]] for i, value in enumerate(['Election Date', *returnColumns])})
                                        ])
        
        
    if(len(electionReturnsDatatableForFigure)>0):    
        hoverCompoundReturnsList = cumulativeReturnsAggregate
        hoverTextMessageElectionChart = [
                                            f'Election State: {electionState}' + '<br>'+
                                            f'Symbol: {symbolNameToPlotValue}' + '<br>' +
                                            f'Day: {returnColumns[i]}' + '<br>' + 
                                            f'Return Percentage: {hoverCompoundReturnsList[i]}' + '%'
                                            for i in range(len(hoverCompoundReturnsList))
                                        ]
        electionReturnsFigure.add_scatter(
            x = electionReturnsDatatableForFigure['Date'],
            y = electionReturnsDatatableForFigure['SuperimposedReturn'],
            text = hoverTextMessageElectionChart,
            hoverinfo='text',
        )
        electionReturnsFigure.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        electionReturnsFigure.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        electionReturnsFigure.update_layout(
            title='Superimposed Returns For Elections',
            xaxis_title = 'Days',
            yaxis_title = 'Compounded Percentage Return', 
            yaxis_tickformat='.2f',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        electionReturnsFigure.add_hline(y=0, line_width=2, line_dash='solid', line_color='grey')
    

    cumulativeReturnsDatatableToPlot = cumulativeReturnsDatatable.to_dict('records')
    global electionCumulativeReturnsDatatableToDownload
    electionCumulativeReturnsDatatableToDownload = dcc.send_data_frame(cumulativeReturnsDatatable.to_csv, f'youngTurtle_electionCumulativeReturns.csv')
    
    return [electionReturnsDatatableToPlot, cumulativeReturnsDatatableToPlot, electionReturnsFigure]


@callback(
    Output(component_id='daily_electionDatatable_download_csv', component_property='data'),
    Input('daily_electionDatatable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def electionDataTableDownload(
    electionDataTableDownloadbutton
):
    return electionDatatableToDownload


@callback(
    Output(component_id='daily_electionCumulativeReturnsDatatable_download_csv', component_property='data'),
    Input('daily_electionCumulativeReturnsDatatable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def electionDataTableDownload(
    electionCumulativeReturnsDataTableDownloadbutton
):
    return electionCumulativeReturnsDatatableToDownload


@callback(
    Output(component_id='daily_exitPollReturnsDatatable', component_property='data'),
    [
        Input('daily_electionSymbolNameToPlot', 'value'),Input('daily_electionDateRange', 'start_date'), 
        Input('daily_electionDateRange', 'end_date'),  Input('daily_electionMonthOutlierToggle', 'value'),
        Input('daily_exitPollReturnsValueBasis', 'value'), 
    ]
)
def exitPollReturns(symbolNameToPlotValue, startDate, 
                    endDate, electionMonthOutlierToggle,
                    exitPollReturnsValueBasis
):
    exitPollsDatatable = pd.DataFrame()
    exitPollsDatatableToPlot = exitPollsDatatable.to_dict('records')

    # Read Symbol File
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
    
    for column in symboldf.columns:
        if symboldf[column].dtype == 'object' and all(symboldf[column].astype(str).str.lower().isin(['true', 'false'])):
            symboldf[column] = symboldf[column].astype(bool)
    
    
    # Get Election and Exit Poll Dates
    electionDatesList = list()
    exitPollDatesList = list()
    electionDf = pd.DataFrame()
    
    try:
        electionDf = pd.read_csv('./elections/' + 'INDIA.csv')
    except:
        print("Election File not found")
    
    if(len(electionDf)>0):
        electionDatesSeries = electionDf['Date'].dropna()
        electionDatesSeries = pd.to_datetime(electionDatesSeries, format='%Y-%m-%d')
        electionDatesSeries = electionDatesSeries[(electionDatesSeries>=symboldf['Date'].min())
                                    & (electionDatesSeries<=symboldf['Date'].max())
                                ]
        if(electionMonthOutlierToggle==1):
                electionDatesSeries = electionDatesSeries[pd.to_datetime(electionDatesSeries, format='%Y-%m-%d').dt.month == 5]
        electionDatesList = electionDatesSeries.values
        
        exitPollDatesSeries = electionDf['Exit Poll Date'].dropna()
        exitPollDatesSeries = pd.to_datetime(exitPollDatesSeries, format='%Y-%m-%d')
        exitPollDatesSeries = exitPollDatesSeries[
                                (exitPollDatesSeries>=symboldf['Date'].min())
                                & (exitPollDatesSeries<=symboldf['Date'].max())
                                ]
        if(electionMonthOutlierToggle==1):
            exitPollDatesSeries = exitPollDatesSeries[pd.to_datetime(exitPollDatesSeries, format='%Y-%m-%d').dt.month == 5]
        exitPollDatesList = exitPollDatesSeries.values
       
    # Election Day Returns
    returnDfIndex = 0
    returnDfColumns = ['Election Date', 'Exit Poll Day Returns', 'Election Day Returns' ]
    exitPollsDatatable = pd.DataFrame(columns=returnDfColumns)
    dateIndex = None
    
    for electionDate in electionDatesList:
        electionDate = pd.to_datetime(electionDate, format='%Y-%m-%d')
        exitPollsDatatable.loc[returnDfIndex] = [pd.to_datetime(electionDate, format='%Y-%m-%d').strftime('%d-%m-%Y'), np.NaN, np.NaN]
        # If Election Date not present, get next Date 
        if(electionDate not in symboldf['Date'].values):
            while(electionDate not in symboldf['Date'].values):
                electionDate = electionDate + timedelta(days=1)
        
        electionDate = pd.to_datetime(electionDate, format='%Y-%m-%d')
        dateIndex = symboldf[symboldf['Date']==electionDate].index.values[0]

        if(exitPollReturnsValueBasis==1):
            exitPollsDatatable.at[returnDfIndex,returnDfColumns[2]] = symboldf.loc[dateIndex]['ReturnPercentage']
        else:
            startOpen = symboldf.loc[dateIndex]['Open']
            endClose = symboldf.loc[dateIndex]['Close']
            exitPollsDatatable.at[returnDfIndex,returnDfColumns[2]] = round(((endClose - startOpen)/startOpen)*100, 2)
        
        returnDfIndex = returnDfIndex + 1

    # Exit Poll Day Returns
    if(len(electionDatesList) == len(exitPollDatesList)):
        returnDfIndex = 0
    else:
        returnDfIndex = len(electionDatesList) - len(exitPollDatesList)
        
   
    exitPollDateIndex = None
    for exitPollDate in exitPollDatesList:
        exitPollDate = pd.to_datetime(exitPollDate, format='%Y-%m-%d')  
        # If Exit Poll Data candle is missing - consider next day candle
        if(exitPollDate not in symboldf['Date'].values):
            while(exitPollDate not in symboldf['Date'].values):
                exitPollDate = exitPollDate + timedelta(days=1)
        exitPollDate = pd.to_datetime(exitPollDate, format='%Y-%m-%d') 
        exitPollDateIndex = symboldf[symboldf['Date']==exitPollDate].index.values[0]  
        
        if(exitPollReturnsValueBasis==1):
            exitPollsDatatable.at[returnDfIndex,returnDfColumns[1]] = symboldf.loc[exitPollDateIndex]['ReturnPercentage']
        else:
            startOpen = symboldf.loc[exitPollDateIndex]['Open']
            endClose = symboldf.loc[exitPollDateIndex]['Close']
            exitPollsDatatable.at[returnDfIndex,returnDfColumns[1]] = round(((endClose - startOpen)/startOpen)*100, 2)
        
        returnDfIndex = returnDfIndex + 1    
    
    exitPollsDatatableToPlot = exitPollsDatatable.to_dict('records')
    
    if(len(exitPollsDatatable)>0):
        exitPollsDatatable = exitPollsDatatable.set_index('Election Date')
    
    global exitPollReturnsDatatableToDownload
    exitPollReturnsDatatableToDownload = dcc.send_data_frame(exitPollsDatatable.to_csv, 'youngTurtle_exitPollAndElectionDayReturns.csv')
    
    return exitPollsDatatableToPlot

@callback(
    Output(component_id='daily_exitPollReturnsDatatable_download_csv', component_property='data'),
    Input('daily_exitPollReturnsDatatable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def midElectionsDatatableDownload(
    exitPollReturnsDataTableDownloadbutton
):
    return exitPollReturnsDatatableToDownload



@callback(
    Output(component_id='daily_midElectionDatatable', component_property='data'),
    [
        Input('daily_electionState', 'value'), Input('daily_electionSymbolNameToPlot', 'value'),
        Input('daily_electionDateRange', 'start_date'), Input('daily_electionDateRange', 'end_date'), 
        Input('daily_electionMidYearTrendType', 'value'),     
    ]
)

def displayMidElectionResults( 
electionState, symbolNameToPlotValue, 
startDate, endDate,
trendType
):
    # Read Symbol File and perform necessary operations
    try:
        symboldf = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/1_Daily.csv')
        symboldf['Date'] = pd.to_datetime(symboldf['Date'], format='%Y-%m-%d')
        symboldf['ExpiryWeeklyDate'] = pd.to_datetime(symboldf['ExpiryWeeklyDate'], format='%Y-%m-%d')
        symboldf['MondayWeeklyDate'] = pd.to_datetime(symboldf['MondayWeeklyDate'], format='%Y-%m-%d')
        symboldf = symboldf.dropna()
        symboldf = symboldf[(symboldf['Date'] >= startDate) & (symboldf['Date'] <= endDate)].reset_index(drop=True)
        symboldf['Year'] = symboldf['Date'].dt.year
    except:
        print(f"Error fetching {symbolNameToPlotValue} file")
        print()
    
    for column in symboldf.columns:
        if symboldf[column].dtype == 'object' and all(symboldf[column].astype(str).str.lower().isin(['true', 'false'])):
            symboldf[column] = symboldf[column].astype(bool)
    
    # Read Election Dates   
    try:
        electionDates = pd.read_csv('./elections/' + electionState + '.csv')
        electionDates = electionDates['MidElectionYears'].dropna()
        electionDates = pd.to_datetime(electionDates, format='%Y').dt.year
        electionDates = electionDates[
                            (electionDates>=symboldf['Date'].min().year)
                            & ((electionDates<=symboldf['Date'].max().year))
                        ].to_list()
    except:
        print(f"Error fetching the electionDates for {electionState}")
        print()
    
    # Manually make mid Election Years List by incrementing Election Date year by 2 and 3 for India, and 2 for USA
    midElectionYear = electionDates
    
    # Datatables Initial Declaration
    midElectionYearReturns = pd.DataFrame()
    global midElectionDatatableToDownload
    midElectionYearReturnsPlot = midElectionYearReturns.to_dict('records')
    
    # Group it by year
    grouped_df = symboldf.groupby('Year')
    prevClose = None
    columnsValueDict = dict()   # For datatable; Optimized using Dictionary using Year as Key and Max drop as Value
    yearlyMaxDrop = 0 
    bearDrop = -18          #Fixing Bear Drop criteria as -18% atleast
    
    for key, data in grouped_df:
        data = data.reset_index(drop=True)
        if(key in midElectionYear and prevClose!=None): #If Previous year Close is available and key/year is in manually calculated Mid-Election year List
            yearlyMaxDrop = ((data['Low'].min() - prevClose)/prevClose) * 100
            
            if(trendType=='Bear' and yearlyMaxDrop <= bearDrop):
                columnsValueDict[key] = round(yearlyMaxDrop, 2)
            elif(trendType=='Any'):
                columnsValueDict[key] = round(yearlyMaxDrop, 2)
            else:
                columnsValueDict[key] = np.NaN
        
        prevClose = data.loc[len(data)-1]['Close']  
    
    if(len(columnsValueDict)>0):
        midElectionYearReturns = pd.DataFrame(columnsValueDict.items(), columns=['Mid Election Year', 'Max Drop wrt. Prev Year Close'])
        midElectionYearReturns = midElectionYearReturns.dropna()
        midElectionYearReturnsPlot = midElectionYearReturns.to_dict('records')
    else:
        print("Data insufficient for Mid-Election-Years Max Drop Calculations")
        print()
    
    midElectionDatatableToDownload = dcc.send_data_frame(midElectionYearReturns.set_index('Mid Election Year').to_csv, 'youngTurtle_midElectionReturns.csv')
    
    return midElectionYearReturnsPlot


@callback(
    Output(component_id='daily_midElectionDatatable_download_csv', component_property='data'),
    Input('daily_midElectionDatatable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def midElectionsDatatableDownload(
    midElectionDataTableDownloadbutton
):
    return midElectionDatatableToDownload
