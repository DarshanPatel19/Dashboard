from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import os
import math
from itertools import zip_longest
import random
from helper import symbolNamesToDropdown, watchListToDropDown, specialDaysToDropdown, monthFullNames, \
    weekDays, tradingDays, calenderDays, colorDict, \
    getDataTableForPlot, getDataTableStatistics, getMonthNumber, getHistoricTrendingDays, \
    filterDataFrameFromHelper, getTrendingDays, generatePerformanceTable, \
    getRecentDayReturnPercentage, getRecentWeekReturnPercentage, getRecentMonthReturnPercentage, \
    maximumConsecutiveValues

phenomenaBackTestTradeListDownload = pd.DataFrame()
phenomenaBackTestReportDownload = pd.DataFrame()
query1DataTableDownload = pd.DataFrame()

phenomenaBackTesterLayout = html.Div([
    html.Br(), html.Br(),
    html.H2('Data Parameters'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Symbol'), width=5, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('Select Date Range'), width=5, align='left', style={'color': '#00218fa1'})
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='phenomenaBackTester_symbolNameToPlot',
                                   options=symbolNamesToDropdown,
                                   value=symbolNamesToDropdown[0],
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.DatePickerRange(id='phenomenaBackTester_dataRange',
                                min_date_allowed=date(1970, 1, 1), max_date_allowed=date(2025, 12, 31),
                                start_date=date(2016, 1, 1), end_date=date(2023, 12, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Even/Odd/Leap Years'), width=5, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('Select Specific Month'), width=6, align='left', style={'color': '#00218fa1'})
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='phenomenaBackTester_evenOddYears',
                           inline=True,
                           options=[dict(label='All Years', value='All'),
                                    dict(label='Even Years only', value=True),
                                    dict(label='Odd Years only', value=False),
                                    dict(label='Leap Years only', value = 2)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.Slider(id='phenomenaBackTester_specificMonthSelection',
                       min=0, max=12, step=1,
                       marks={
                           0: {'label': 'Disable', 'style': {'color': 'red'}},
                           1: {'label': 'Jan', 'style': {'color': 'black'}}, 2: {'label': 'Feb', 'style': {'color': 'black'}},
                           3: {'label': 'Mar', 'style': {'color': 'black'}}, 4: {'label': 'Apr', 'style': {'color': 'black'}},
                           5: {'label': 'May', 'style': {'color': 'black'}}, 6: {'label': 'Jun', 'style': {'color': 'black'}},
                           7: {'label': 'Jul', 'style': {'color': 'black'}}, 8: {'label': 'Aug', 'style': {'color': 'black'}},
                           9: {'label': 'Sep', 'style': {'color': 'black'}}, 10: {'label': 'Oct', 'style': {'color': 'black'}},
                           11: {'label': 'Nov', 'style': {'color': 'black'}}, 12: {'label': 'Dec', 'style': {'color': 'black'}}
                       },
                       dots=False, updatemode='drag',
                       tooltip=dict(always_visible=True, placement='top'),
                       value=0,
                       included=False,
                       persistence=True, persistence_type='session'),
            width=6, align='left'
        ),
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Specific Expiry Weeks(Monthly Count)'), width=5, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('Select Specific Monday Weeks(Monthly Count)'), width=5, align='left', style={'color': '#00218fa1'}),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Slider(id='phenomenaBackTester_specificExpiryWeekMonthlySelection',
                                 min=0, max=5, step=1,
                                 marks={
                                     0: {'label': 'Disable', 'style': {'color': 'red'}},
                                     1: {'label': '1', 'style': {'color': 'black'}}, 2: {'label': '2', 'style': {'color': 'black'}},
                                     3: {'label': '3', 'style': {'color': 'black'}}, 4: {'label': '4', 'style': {'color': 'black'}},
                                     5: {'label': '5', 'style': {'color': 'black'}}
                                 },
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='top'),
                                 included=False,
                                 value=0,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='phenomenaBackTester_specificMondayWeekMonthlySelection',
                                 min=0, max=5, step=1,
                                 marks={
                                     0: {'label': 'Disable', 'style': {'color': 'red'}},
                                     1: {'label': '1', 'style': {'color': 'black'}}, 2: {'label': '2', 'style': {'color': 'black'}},
                                     3: {'label': '3', 'style': {'color': 'black'}}, 4: {'label': '4', 'style': {'color': 'black'}},
                                     5: {'label': '5', 'style': {'color': 'black'}}
                                 },
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='top'),
                                 included=False,
                                 value=0,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    html.H2('Strategy Parameters'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Enter Initial Capital'), width=5, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('Select Risk Free Rate(%)'), width=5, align='left', style={'color': '#00218fa1'}),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Input(id='phenomenaBackTester_initialCapital',
                                type='number', value=10000000,
                                placeholder='Enter Initial Capital',
                                style={'width': '450px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-left': '20px', 'padding-top': '15px'}),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='phenomenaBackTester_riskFreeRate',
                                 min=0, max=10,
                                 marks={str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(0, 11, 1)},
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='top'),
                                 included=False,
                                 value=5.4,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Trade Type'), width=5, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('Enter Brokerage(%)'), width=5, align='left', style={'color': '#00218fa1'}),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='phenomenaBackTester_tradeType',
                           inline=True,
                           options=[dict(label='Long Trades', value='longTrades'),
                                    dict(label='Short Trades', value='shortTrades')],
                           value='longTrades',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='phenomenaBackTester_brokerage',
                                type='number', value=0.04,
                                placeholder='Enter Brokerage',
                                style={'width': '450px'},
                                min=0, max=5, step=0.01,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-left': '20px', 'padding-top': '15px'}),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Phenomena Days'), width=10, align='left', style={'color': '#00218fa1'}),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.RangeSlider(id='phenomenaBackTester_phenomenaDays',
                                      min=-10, max=23, step=1,
                                      marks={
                                          str(h): {'label': str(h), 'style': {'color': 'black'}} if h != 0 else {'label': None}
                                          for h in range(-10, 24, 1)
                                      },
                                      dots=False, updatemode='drag', allowCross=False,
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      value=[-5, 2],
                                      persistence=True, persistence_type='session')],
                     style=dict(width='95%')),
            width=10, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    html.Br(),
    dbc.Button(id='phenomenaBackTester_outputTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='phenomenaBackTester_outputTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='phenomenaBackTester_tradeList',
                                           editable=True, page_size=100,
                                           sort_action='native', sort_mode='multi',
                                              style_data_conditional=[{
                                                  'if': {
                                                      'column_id': 'Number',
                                                  },
                                                  'minWidth': '80px', 'maxWidth': '15px',
                                                  'backgroundColor': 'lightgrey',
                                                  'color': 'black',
                                                  'fontWeight': 'bold'
                                              }],
                                           style_cell=dict(
                                               whiteSpace='pre-line'
                                              ),
                                           style_table={
                                               'overflowX': 'scroll'
                                              },
                                           style_data=dict(
                                               minWidth='120px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='white', color='black'
                                              ),
                                           style_header=dict(
                                               minWidth='120px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold'
                                              ),
                                           ),],
                     style=dict(width='100%')),
            width=11, align='left'
        )
    ]),

    html.Br(),
    dbc.Button(id='phenomenaBackTester_reportTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='phenomenaBackTester_reportTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='phenomenaBackTester_report',
                                           editable=True, page_size=100,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'Parameters',
                                               },
                                               'minWidth': '80px', 'maxWidth': '15px',
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold'
                                           }],
                                           style_cell=dict(
                                               whiteSpace='pre-line'
                                           ),
                                           style_data=dict(
                                               maxWidth='200px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='white', color='black'
                                           ),
                                           style_header=dict(
                                               maxWidth='200px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold'
                                           ),
                                           ),],
                     style=dict(width='100%')),
            width=5, align='left'
        )
    ]),

    # QUERY ONE
    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Query One'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Weekday'), width=4, align='left'),
        dbc.Col(html.H6('Select Trading Month day'), width=4, align='left'),
        dbc.Col(html.H6('Select Calender Month day'), width=4, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_selectWeekdayToQuery1',
                                   options=weekDays,
                                   value=['Monday', 'Friday'], multi=True,
                                   clearable=False, maxHeight=250,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_selectTradingdayToQuery1',
                                   options=tradingDays,
                                   value=[1], multi=True,
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_selectCalenderdayToQuery1',
                                   options=calenderDays,
                                   value=[1, 2, 3, 4, 5], multi=True,
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
        )
    ]),

    html.Br(), html.Br(),
    dbc.Button(id='daily_query1DataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_query1DataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_query1DataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'index',
                                               },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold',
                                               'minWidth': '12px'
                                           }],
                                           style_cell=dict(
                                               whiteSpace='pre-line'
                                           ),
                                           style_header=dict(
                                               width='8px', minWidth='8px', maxWidth='8px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold'
                                           ),
                                           style_data=dict(
                                               width='8px', minWidth='8px', maxWidth='8px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='white', color='black'
                                           )),],
                     style=dict(width='100%')),
            width=10, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    
    # HEAT MAPS
    html.H2('Heatmap - Average Daily Returns'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Heatmap Type'), width=6, align='left'),
        dbc.Col(html.H6('Show Annotation Values'), width=4, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_heatmap1Type',
                           inline=True,
                           options=[dict(label='Trading Month Days - Weekdays', value='TradingMonthDaysVsWeekdays'),
                                    dict(label='Calender Month Days - Weekdays', value='CalenderMonthDaysVsWeekdays')],
                           value='TradingMonthDaysVsWeekdays',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=6, align='left'
        ),
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='daily_heatmap1AnnotationValueSwitch',  # type:ignore
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=4, align='left'
        )
    ]),
    dcc.Graph(id='daily_heatmap1TypeChart', style=dict(height='90vh')),
    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    
    # WALK FORWARD SUPERIMPOSED RETURN CHART
    html.H2('Walk Forward Superimposed Returns Chart Inputs'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('In the Sample Date Range'), width=7, align='left'),
        dbc.Col(html.H6('Out of the Sample Date Range'), width=4, align='left')
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(
            dcc.DatePickerRange(id='daily_inTheSampleDataRange',
                                min_date_allowed=date(1970, 1, 1), max_date_allowed=date(2025, 12, 31),
                                start_date=date(2016, 1, 1), end_date=date(2019, 12, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=7, align='left'
        ),
        dbc.Col(
            dcc.DatePickerRange(id='daily_outOfTheSampleDataRange',
                                min_date_allowed=date(1970, 1, 1), max_date_allowed=date(2025, 12, 31),
                                start_date=date(2020, 1, 1), end_date=date(2022, 12, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Superimposed Chart'), width=7, align='left'),
        dbc.Col(html.H6('Select Symbol'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_walkForwardSuperimposedChartType',
                           inline=True,
                           options=[dict(label='Calendar Year Days', value='CalenderYearDay'),
                                    dict(label='Trading Year Days', value='TradingYearDay'),
                                    dict(label='Calendar Month Days', value='CalenderMonthDay'),
                                    dict(label='Trading Month Days', value='TradingMonthDay'),
                                    dict(label='Weekdays', value='Weekday')],
                           value='CalenderYearDay',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=7, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_walkForwardSuperimposedChartSymbol',
                                   options=symbolNamesToDropdown,
                                   value = [],
                                   multi=True, 
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.H2('Walk Forward Superimposed Returns Chart Output'),
    dcc.Graph(id='daily_walkForwardSuperimposedChart', style=dict(height='90vh')),
    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    
    # End of Dash components
    
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),

],
    style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)


@callback(
    [
        Output(component_id='phenomenaBackTester_tradeList', component_property='data'),
        Output(component_id='phenomenaBackTester_report', component_property='data'),
    ],
    [
        Input('phenomenaBackTester_symbolNameToPlot', 'value'), 
        Input('phenomenaBackTester_dataRange', 'start_date'), 
        Input('phenomenaBackTester_dataRange', 'end_date'),
        Input('phenomenaBackTester_evenOddYears', 'value'), 
        Input('phenomenaBackTester_specificMonthSelection', 'value'),
        Input('phenomenaBackTester_specificExpiryWeekMonthlySelection', 'value'), 
        Input('phenomenaBackTester_specificMondayWeekMonthlySelection', 'value'),
        Input('phenomenaBackTester_initialCapital', 'value'), 
        Input('phenomenaBackTester_riskFreeRate', 'value'),
        Input('phenomenaBackTester_tradeType', 'value'), 
        Input('phenomenaBackTester_brokerage', 'value'),
        Input('phenomenaBackTester_phenomenaDays', 'value'),

    ]
)
def display_phenomenaBackTester(
    symbolNameToPlot, scannerStartDate, scannerEndDate,
    evenOddYearsValue, specificMonthValue,
    specificExpiryWeekMonthlyValue, specificMondayWeekMonthlyValue,
    initialCapitalValue, riskFreeRateValue,
    tradeType, brokerageValue,
    phenomenaDaysValues
):

    tradeListColumns = [
        'Number', 'Symbol', 'Trade',
        'Entry Date', 'Entry Price', 'Exit Date', 'Exit Price', 'Contracts', 'Entry Value', 'Exit Value',
        'Profit Points', 'Profit Percentage', 'Profit Value',
        'Profit Points(With Brokerage)', 'Profit Percentage(With Brokerage)', 'Profit Value(With Brokerage)',
        'Cumulative Profit', 'Cumulative Profit(With Brokerage)', 'Available Cash',
        'Bars Held', 'Profit/Bar',
        'MAE Points', 'MFE Points', 'MAE Percentage', 'MFE Percentage',
        'Net Profit%', 'Max Profit%', 'Max Available Cash', 'DD%', 'DD'
    ]
    statisticsReport = [
        'Initial Capital', 'Ending Capital', 'Net Profit', 'Net Profit %', 'Annual Return %', 'Total Transaction Costs',
        'Total Trades', 'Average Profit/Loss', 'Average Profit/Loss %', 'Average Bars Held',
        'Total Wins', 'Total Profit', 'Average Profit', 'Average Profit %', 'Average Bars Held in Profit', 'Maximum Consecutive Wins', 'Largest Win', 'Bars in Largest Win',
        'Total Losses', 'Total Loss', 'Average Loss', 'Average Loss %', 'Average Bars Held in Loss', 'Maximum Consecutive Losses', 'Largest Loss', 'Bars in Largest Loss',
        'Maximum Trade Drawdown', 'Maximum Trade Drawdown %', 'Maximum System Drawdown', 'Maximum System Drawdown %',
        'Recovery Factor', 'CAR/MaxDD', 'Profit Factor', 'Payoff Ratio',
    ]

    phenomenaBackTestTradeList = pd.DataFrame(columns=tradeListColumns)
    phenomenaBackTestReport = pd.DataFrame(columns=statisticsReport)

    global phenomenaBackTestTradeListDownload
    global phenomenaBackTestReportDownload
    phenomenaDaysValueStart, phenomenaDaysValueEnd = phenomenaDaysValues

    df = pd.read_csv('./Symbols/' + symbolNameToPlot + '/1_Daily.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
    df['Year'] = df['Date'].dt.year
    df = df.dropna()
    
    # choose date range
    df = df[(df['Date'] >= scannerStartDate) & (df['Date'] <= scannerEndDate)]

    # choose even/odd years
    if (evenOddYearsValue != 'All'):
        if(evenOddYearsValue != 2):
            df = df[df['EvenYear'] == evenOddYearsValue]
        else:
            df = df[(df['Date'].dt.year % 4 == 0) & ((df['Date'].dt.year % 100 != 0) | (df['Date'].dt.year % 400 == 0))]

    # choose specific month
    if (specificMonthValue != 0):
        df = df[df['Date'].dt.month == specificMonthValue]

    # choose monday/expiry weeks
    if (specificExpiryWeekMonthlyValue != 0):
        df = df[df['ExpiryWeekNumberMonthly'] == specificExpiryWeekMonthlyValue]
    if (specificMondayWeekMonthlyValue != 0):
        df = df[df['MondayWeekNumberMonthly'] == specificMondayWeekMonthlyValue]

    if ((len(df) > 0) & (phenomenaDaysValueEnd > 0)):

        monthLastDates = df[df['Date'].dt.month != df['Date'].shift(-1).dt.month][:-1]['Date'].to_list()
        minRequiredLengthOfTable = (abs(phenomenaDaysValueStart)+phenomenaDaysValueEnd) if phenomenaDaysValueStart < 1 else (phenomenaDaysValueEnd-phenomenaDaysValueStart+1)
        tradeNumber = 0
        highestPrice, lowestPrice = 0, 0

        for monthLastDate in monthLastDates:
            if (phenomenaDaysValueStart < 0):
                tempDataframe = pd.concat([
                    df[df['Date'] <= monthLastDate][phenomenaDaysValueStart:],
                    df[df['Date'] > monthLastDate][0:phenomenaDaysValueEnd]
                ])
            else:
                tempDataframe = df[df['Date'] > monthLastDate][phenomenaDaysValueStart-1:phenomenaDaysValueEnd]
            if (len(tempDataframe) != minRequiredLengthOfTable):
                continue
            else:
                tradeNumber = tradeNumber + 1
                highestPrice = max(tempDataframe.iloc[0]['Close'], *tempDataframe['High'][1:].to_list())
                lowestPrice = min(tempDataframe.iloc[0]['Close'], *tempDataframe['Low'][1:].to_list())
                tradeKeyValues = {
                    'Number': [tradeNumber],
                    'Symbol': symbolNameToPlot,
                    'Trade': 'Long' if tradeType == 'longTrades' else 'Short',
                    'Entry Date': tempDataframe.iloc[0]['Date'],
                    'Entry Price': tempDataframe.iloc[0]['Close'],
                    'Exit Date': tempDataframe.iloc[-1]['Date'],
                    'Exit Price': tempDataframe.iloc[-1]['Close'],
                    'Contracts': 0,
                    'Entry Value': 0,
                    'Exit Value': 0,
                    'Profit Points': 0,
                    'Profit Percentage': 0,
                    'Profit Value': 0,
                    'Profit Points(With Brokerage)': 0,
                    'Profit Percentage(With Brokerage)': 0,
                    'Profit Value(With Brokerage)': 0,
                    'Cumulative Profit': 0,
                    'Cumulative Profit(With Brokerage)': 0,
                    'Available Cash': 0,
                    'Bars Held': minRequiredLengthOfTable,
                    'Profit/Bar': 0,
                    'MAE Points': (lowestPrice-tempDataframe.iloc[0]['Close']) if tradeType == 'longTrades' else (tempDataframe.iloc[0]['Close']-highestPrice),
                    'MFE Points': (highestPrice-tempDataframe.iloc[0]['Close']) if tradeType == 'longTrades' else (tempDataframe.iloc[0]['Close']-lowestPrice),
                    'MAE Percentage': 0,
                    'MFE Percentage': 0,
                    'Net Profit%': 0,
                    'Max Profit%': 0,
                    'Max Available Cash': 0,
                    'DD%': 0,
                    'DD': 0
                }
                phenomenaBackTestTradeList = pd.concat([
                    phenomenaBackTestTradeList,
                    pd.DataFrame(tradeKeyValues)
                ], ignore_index=True)

    if (tradeType == 'longTrades'):
        phenomenaBackTestTradeList['Profit Points'] = phenomenaBackTestTradeList['Exit Price'] - phenomenaBackTestTradeList['Entry Price']
    else:
        phenomenaBackTestTradeList['Profit Points'] = phenomenaBackTestTradeList['Entry Price'] - phenomenaBackTestTradeList['Exit Price']

    phenomenaBackTestTradeList['Profit Percentage'] = (phenomenaBackTestTradeList['Profit Points']*100)/phenomenaBackTestTradeList['Entry Price']
    phenomenaBackTestTradeList['Profit Points(With Brokerage)'] = phenomenaBackTestTradeList['Profit Points'] - ((phenomenaBackTestTradeList['Exit Price'] + phenomenaBackTestTradeList['Entry Price'])*brokerageValue/100)
    phenomenaBackTestTradeList['Profit Percentage(With Brokerage)'] = (phenomenaBackTestTradeList['Profit Points(With Brokerage)']*100)/phenomenaBackTestTradeList['Entry Price']
    phenomenaBackTestTradeList['MAE Percentage'] = (phenomenaBackTestTradeList['MAE Points']*100)/phenomenaBackTestTradeList['Entry Price']
    phenomenaBackTestTradeList['MFE Percentage'] = (phenomenaBackTestTradeList['MFE Points']*100)/phenomenaBackTestTradeList['Entry Price']

    for index in range(0, len(phenomenaBackTestTradeList)):
        if (index == 0):
            phenomenaBackTestTradeList.loc[0, 'Contracts'] = int(initialCapitalValue/phenomenaBackTestTradeList.iloc[0]['Entry Price'])
            phenomenaBackTestTradeList.loc[0, [
                'Entry Value', 'Exit Value', 'Profit Value', 'Profit Value(With Brokerage)',
                'Cumulative Profit', 'Cumulative Profit(With Brokerage)', 'Available Cash', 'Profit/Bar'
            ]] = [
                phenomenaBackTestTradeList.iloc[0]['Contracts']*phenomenaBackTestTradeList.iloc[0]['Entry Price'],
                phenomenaBackTestTradeList.iloc[0]['Contracts']*phenomenaBackTestTradeList.iloc[0]['Exit Price'],
                phenomenaBackTestTradeList.iloc[0]['Contracts']*phenomenaBackTestTradeList.iloc[0]['Profit Points'],
                phenomenaBackTestTradeList.iloc[0]['Contracts']*phenomenaBackTestTradeList.iloc[0]['Profit Points(With Brokerage)'],
                phenomenaBackTestTradeList.iloc[0]['Contracts']*phenomenaBackTestTradeList.iloc[0]['Profit Points'],
                phenomenaBackTestTradeList.iloc[0]['Contracts']*phenomenaBackTestTradeList.iloc[0]['Profit Points(With Brokerage)'],
                initialCapitalValue+(phenomenaBackTestTradeList.iloc[0]['Contracts']*phenomenaBackTestTradeList.iloc[0]['Profit Points(With Brokerage)']),
                phenomenaBackTestTradeList.iloc[0]['Contracts']*phenomenaBackTestTradeList.iloc[0]['Profit Points(With Brokerage)']/phenomenaBackTestTradeList.iloc[0]['Bars Held'],
            ]
        else:
            phenomenaBackTestTradeList.loc[index, 'Contracts'] = int(phenomenaBackTestTradeList.iloc[index-1]['Available Cash']/phenomenaBackTestTradeList.iloc[index]['Entry Price'])
            phenomenaBackTestTradeList.loc[index, 'Available Cash'] = phenomenaBackTestTradeList.iloc[index-1]['Available Cash']+(phenomenaBackTestTradeList.iloc[index]['Contracts']*phenomenaBackTestTradeList.iloc[index]['Profit Points(With Brokerage)'])

    phenomenaBackTestTradeList['Entry Value'] = phenomenaBackTestTradeList['Contracts']*phenomenaBackTestTradeList['Entry Price']
    phenomenaBackTestTradeList['Exit Value'] = phenomenaBackTestTradeList['Contracts']*phenomenaBackTestTradeList['Exit Price']
    phenomenaBackTestTradeList['Profit Value'] = phenomenaBackTestTradeList['Contracts']*phenomenaBackTestTradeList['Profit Points']
    phenomenaBackTestTradeList['Profit Value(With Brokerage)'] = phenomenaBackTestTradeList['Contracts']*phenomenaBackTestTradeList['Profit Points(With Brokerage)']
    phenomenaBackTestTradeList['Cumulative Profit'] = phenomenaBackTestTradeList['Profit Value'].cumsum()
    phenomenaBackTestTradeList['Cumulative Profit(With Brokerage)'] = phenomenaBackTestTradeList['Profit Value(With Brokerage)'].cumsum()
    phenomenaBackTestTradeList['Profit/Bar'] = phenomenaBackTestTradeList['Profit Value(With Brokerage)']/phenomenaBackTestTradeList['Bars Held']

    phenomenaBackTestTradeList['Net Profit%'] = (phenomenaBackTestTradeList['Available Cash']*100)/initialCapitalValue
    phenomenaBackTestTradeList['Max Profit%'] = phenomenaBackTestTradeList['Net Profit%'].cummax()
    phenomenaBackTestTradeList['Max Available Cash'] = phenomenaBackTestTradeList['Available Cash'].cummax()
    phenomenaBackTestTradeList['DD%'] = (phenomenaBackTestTradeList['Available Cash']*100/phenomenaBackTestTradeList['Max Available Cash'])-100
    phenomenaBackTestTradeList['DD'] = phenomenaBackTestTradeList['Available Cash']-phenomenaBackTestTradeList['Max Available Cash']

    phenomenaBackTestTradeList['Entry Date'] = pd.to_datetime(phenomenaBackTestTradeList['Entry Date']).dt.strftime('%d-%m-%Y')
    phenomenaBackTestTradeList['Exit Date'] = pd.to_datetime(phenomenaBackTestTradeList['Exit Date']).dt.strftime('%d-%m-%Y')

    phenomenaBackTestTypes = {
        'Number': int,
        'Symbol': str,
        'Trade': str,
        'Entry Date': str,
        'Entry Price': float,
        'Exit Date': str,
        'Exit Price': float,
        'Contracts': int,
        'Entry Value': float,
        'Exit Value': float,
        'Profit Points': float,
        'Profit Percentage': float,
        'Profit Value': float,
        'Profit Points(With Brokerage)': float,
        'Profit Percentage(With Brokerage)': float,
        'Profit Value(With Brokerage)': float,
        'Cumulative Profit': float,
        'Cumulative Profit(With Brokerage)': float,
        'Available Cash': float,
        'Bars Held': int,
        'Profit/Bar': float,
        'MAE Points': float,
        'MFE Points': float,
        'MAE Percentage': float,
        'MFE Percentage': float,
        'Net Profit%': float,
        'Max Profit%': float,
        'Max Available Cash': float,
        'DD%': float,
        'DD': float
    }
    phenomenaBackTestTradeList = phenomenaBackTestTradeList.astype(phenomenaBackTestTypes)

    maximumTradeDrawdown = round(phenomenaBackTestTradeList['Profit Value(With Brokerage)'].min(), 2)
    maximumTradeDrawdownPercentage = round(phenomenaBackTestTradeList.loc[phenomenaBackTestTradeList['Profit Value(With Brokerage)'].idxmin()]['Profit Percentage(With Brokerage)'], 2)
    maximumSystemDrawdown = round(phenomenaBackTestTradeList['DD'].min(), 2)
    maximumSystemDrawdownPercentage = round(phenomenaBackTestTradeList['DD%'].min(), 2)

    phenomenaBackTestTradeList.drop(columns=['Net Profit%', 'Max Profit%', 'Max Available Cash', 'DD%', 'DD'], inplace=True)

    columnsToRoundoff = [
        'Entry Price', 'Exit Price', 'Entry Value', 'Exit Value',
        'Profit Points', 'Profit Percentage', 'Profit Value',
        'Profit Points(With Brokerage)', 'Profit Percentage(With Brokerage)', 'Profit Value(With Brokerage)',
        'Cumulative Profit', 'Cumulative Profit(With Brokerage)', 'Available Cash',
        'Profit/Bar', 'MAE Points', 'MFE Points', 'MAE Percentage', 'MFE Percentage'
    ]
    phenomenaBackTestTradeList[columnsToRoundoff] = phenomenaBackTestTradeList[columnsToRoundoff].round(2)

    endingCapital = round(phenomenaBackTestTradeList.iloc[-1]['Available Cash'], 0)
    netProfitValue = round(phenomenaBackTestTradeList.iloc[-1]['Cumulative Profit(With Brokerage)'], 0)
    netProfitPercentage = round(phenomenaBackTestTradeList.iloc[-1]['Cumulative Profit(With Brokerage)']*100/initialCapitalValue, 2)
    durationInYears = (datetime.strptime(phenomenaBackTestTradeList.iloc[-1]['Exit Date'], '%d-%m-%Y') - datetime.strptime(phenomenaBackTestTradeList.iloc[0]['Entry Date'], '%d-%m-%Y')).days/365.25
    annualReturn = round(100*(math.pow(10, math.log10(endingCapital/initialCapitalValue)/durationInYears)-1), 2)
    totalTransactionCost = round(phenomenaBackTestTradeList.iloc[-1]['Cumulative Profit']-phenomenaBackTestTradeList.iloc[-1]['Cumulative Profit(With Brokerage)'], 0)

    totalTrades = len(phenomenaBackTestTradeList)
    averageProfitLoss = round(phenomenaBackTestTradeList['Profit Value(With Brokerage)'].mean(), 0)
    averageProfitLossPercentage = round(phenomenaBackTestTradeList['Profit Percentage(With Brokerage)'].mean(), 2)
    averageBarsHeld = phenomenaBackTestTradeList['Bars Held'].mean()

    phenomenaBackTestWinnersTradeList = phenomenaBackTestTradeList[phenomenaBackTestTradeList['Profit Value(With Brokerage)'] > 0]
    phenomenaBackTestLossersTradeList = phenomenaBackTestTradeList[phenomenaBackTestTradeList['Profit Value(With Brokerage)'] < 0]
    maximumConsecutiveWins, maximumConsecutiveLosses = maximumConsecutiveValues(phenomenaBackTestTradeList['Profit Value(With Brokerage)'].to_list())

    totalWinners = str(len(phenomenaBackTestWinnersTradeList)) + '(' + str(round(len(phenomenaBackTestWinnersTradeList)/totalTrades*100, 2)) + '%)'
    winnersTotalProfit = round(phenomenaBackTestWinnersTradeList['Profit Value(With Brokerage)'].sum(), 0)
    winnersAverageProfit = round(phenomenaBackTestWinnersTradeList['Profit Value(With Brokerage)'].mean(), 0)
    winnersAverageProfitPercentage = round(phenomenaBackTestWinnersTradeList['Profit Percentage(With Brokerage)'].mean(), 2)
    winnersAverageBarsHeld = phenomenaBackTestWinnersTradeList['Bars Held'].mean()
    largestWin = str(max(phenomenaBackTestWinnersTradeList['Profit Value(With Brokerage)'].to_list())) + '(' + str(max(phenomenaBackTestWinnersTradeList['Profit Percentage(With Brokerage)'].to_list())) + '%)'
    barsInLargestWin = phenomenaBackTestWinnersTradeList.loc[phenomenaBackTestWinnersTradeList['Profit Value(With Brokerage)'].idxmax()]['Bars Held']

    totalLossers = str(len(phenomenaBackTestLossersTradeList)) + '(' + str(round(len(phenomenaBackTestLossersTradeList)/totalTrades*100, 2)) + '%)'
    lossersTotalLoss = round(phenomenaBackTestLossersTradeList['Profit Value(With Brokerage)'].sum(), 0)
    lossersAverageLoss = round(phenomenaBackTestLossersTradeList['Profit Value(With Brokerage)'].mean(), 0)
    lossersAverageLossPercentage = round(phenomenaBackTestLossersTradeList['Profit Percentage(With Brokerage)'].mean(), 2)
    lossersAverageBarsHeld = phenomenaBackTestLossersTradeList['Bars Held'].mean()
    largestLoss = str(min(phenomenaBackTestLossersTradeList['Profit Value(With Brokerage)'].to_list())) + '(' + str(min(phenomenaBackTestLossersTradeList['Profit Percentage(With Brokerage)'].to_list())) + '%)'
    barsInLargestLoss = phenomenaBackTestLossersTradeList.loc[phenomenaBackTestLossersTradeList['Profit Value(With Brokerage)'].idxmin()]['Bars Held']

    recoveryFactor = round(-1*netProfitValue/maximumSystemDrawdown, 2)
    carByMdd = round(-1*annualReturn/maximumSystemDrawdownPercentage, 2)
    profitFactor = round(-1*winnersTotalProfit/lossersTotalLoss, 2)
    payoffRatio = round(-1*winnersAverageProfit/lossersAverageLoss, 2)

    phenomenaBackTestReportDict = {
        'Parameters': statisticsReport[0:34],
        'Values': [
            initialCapitalValue, endingCapital, netProfitValue, netProfitPercentage, annualReturn, totalTransactionCost,
            totalTrades, averageProfitLoss, averageProfitLossPercentage, averageBarsHeld,
            totalWinners, winnersTotalProfit, winnersAverageProfit, winnersAverageProfitPercentage, winnersAverageBarsHeld, maximumConsecutiveWins, largestWin, barsInLargestWin,
            totalLossers, lossersTotalLoss, lossersAverageLoss, lossersAverageLossPercentage, lossersAverageBarsHeld, maximumConsecutiveLosses, largestLoss, barsInLargestLoss,
            maximumTradeDrawdown, maximumTradeDrawdownPercentage, maximumSystemDrawdown, maximumSystemDrawdownPercentage,
            recoveryFactor, carByMdd, profitFactor, payoffRatio
        ]
    }
    phenomenaBackTestReport = pd.DataFrame(phenomenaBackTestReportDict)
    phenomenaBackTestTradeListDownload = dcc.send_data_frame(phenomenaBackTestTradeList.set_index('Number').to_csv, 'Youngturtle_PhenomenaBackTestTradeList.csv')
    phenomenaBackTestReportDownload = dcc.send_data_frame(phenomenaBackTestReport.set_index('Parameters').to_csv, 'Youngturtle_PhenomenaBackTestReport.csv')

    return [
        phenomenaBackTestTradeList.to_dict('records'), phenomenaBackTestReport.to_dict('records')
    ]


@callback(
    [
        Output(component_id='daily_query1DataTable', component_property='data'),
        Output(component_id='daily_heatmap1TypeChart', component_property='figure'),
        Output(component_id='daily_walkForwardSuperimposedChart', component_property='figure'),
    ],
    [
        Input('phenomenaBackTester_symbolNameToPlot', 'value'),Input('phenomenaBackTester_dataRange', 'start_date'), 
        Input('phenomenaBackTester_dataRange', 'end_date'),Input('phenomenaBackTester_evenOddYears', 'value'), 
        Input('phenomenaBackTester_specificMonthSelection', 'value'),Input('phenomenaBackTester_specificExpiryWeekMonthlySelection', 'value'), 
        Input('phenomenaBackTester_specificMondayWeekMonthlySelection', 'value'),Input('daily_selectWeekdayToQuery1', 'value'), 
        Input('daily_selectTradingdayToQuery1', 'value'),Input('daily_selectCalenderdayToQuery1', 'value'),
        Input('daily_heatmap1Type', 'value'),Input('daily_heatmap1AnnotationValueSwitch', 'on'),
        Input('daily_inTheSampleDataRange', 'start_date'),Input('daily_inTheSampleDataRange', 'end_date'),
        Input('daily_outOfTheSampleDataRange', 'start_date'),Input('daily_outOfTheSampleDataRange', 'end_date'),
        Input('daily_walkForwardSuperimposedChartType', 'value'),Input('daily_walkForwardSuperimposedChartSymbol', 'value')
    ]
)
def displayRestOfComponents(symbolNameToPlot, scannerStartDate, 
    scannerEndDate, evenOddYearsValue, 
    specificMonthValue, specificExpiryWeekMonthlyValue, 
    specificMondayWeekMonthlyValue,selectWeekdayToQuery1Value, 
    selectTradingdayToQuery1Value,selectCalenderdayToQuery1Value,
    heatmap1TypeValue, heatmap1AnnotationValueSwitch,
    inTheSampleDataRangeStartDate, inTheSampleDataRangeEndDate,
    outOfTheSampleDataRangeStartDate, outOfTheSampleDataRangeEndDate,
    walkForwardSuperimposedChartTypeValue, walkForwardSuperimposedChartSymbol,
):
    # Backtester, Query and Heatmap
    df = pd.read_csv('./Symbols/' + symbolNameToPlot + '/1_Daily.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
    df['Year'] = df['Date'].dt.year
    df = df.dropna()
    
    # choose date range
    df = df[(df['Date'] >= scannerStartDate) & (df['Date'] <= scannerEndDate)]

    # choose even/odd years
    if (evenOddYearsValue != 'All'):
        df = df[df['EvenYear'] == evenOddYearsValue]

    # choose specific month
    if (specificMonthValue != 0):
        df = df[df['Date'].dt.month == specificMonthValue]

    # choose monday/expiry weeks
    if (specificExpiryWeekMonthlyValue != 0):
        df = df[df['ExpiryWeekNumberMonthly'] == specificExpiryWeekMonthlyValue]
    if (specificMondayWeekMonthlyValue != 0):
        df = df[df['MondayWeekNumberMonthly'] == specificMondayWeekMonthlyValue]

    # Return Datatables and figures
    query1DataTable = pd.DataFrame()
    walkForwardSuperimposedChart = go.Figure()
    global query1DataTableDownload
    
    # Return Dataplot and Figure
    query1DataTableReturnPlot = query1DataTable.to_dict('records')
    heatmap1Chart = go.Figure()
    
    if (len(df) > 0):
        """
            query1 one filter datatable for daily
        """

        query1ReturnPointsForWeekday = np.array(df[
            df['Weekday'].isin(selectWeekdayToQuery1Value)
        ]['ReturnPercentage'].to_list())
        query1ReturnPointsForTradingMonthDay = np.array(df[
            df['TradingMonthDay'].isin(selectTradingdayToQuery1Value)
        ]['ReturnPercentage'].to_list())
        query1ReturnPointsForCalenderMonthDay = np.array(df[
            df['CalenderMonthDay'].isin(selectCalenderdayToQuery1Value)
        ]['ReturnPercentage'].to_list())

        query1StatsForWeekday = getDataTableStatistics(query1ReturnPointsForWeekday)
        query1StatsForTradingMonthDay = getDataTableStatistics(query1ReturnPointsForTradingMonthDay)
        query1StatsForCalenderMonthDay = getDataTableStatistics(query1ReturnPointsForCalenderMonthDay)

        query1DataTable = pd.concat([query1DataTable, query1StatsForWeekday, query1StatsForTradingMonthDay, query1StatsForCalenderMonthDay], axis=1)
        query1DataTable.columns = ['Weekday', 'Trading Month Day', 'Calender Month Day']
        query1DataTableReturnValue = getDataTableForPlot(query1DataTable)
        query1DataTableReturnPlot = query1DataTableReturnValue[0]
        query1DataTableDownload = dcc.send_data_frame(query1DataTableReturnValue[1].to_csv, 'Youngturtle_QueryOne.csv')

        """
            heatmap1 chart for daily only
        """

        heatmap1DataList, totalTradingDays = [], []
        xAxisName, xAxisTitle = '', ''

        if (heatmap1TypeValue == 'TradingMonthDaysVsWeekdays'):
            heatmap1DataList = [[] for i in range(len(weekDays))]
            totalTradingDays = tradingDays
            xAxisName = 'TradingMonthDay'
            xAxisTitle = 'Trading Month Days'
        elif (heatmap1TypeValue == 'CalenderMonthDaysVsWeekdays'):
            heatmap1DataList = [[] for i in range(len(weekDays))]
            totalTradingDays = calenderDays
            xAxisName = 'CalenderMonthDay'
            xAxisTitle = 'Calender Month Day'

        for index1, singleWeekDay in enumerate(weekDays[::-1]):
            for index2, singleTradingDays in enumerate(totalTradingDays):
                meanValue = df[
                    (df['Weekday'] == singleWeekDay) & (df[xAxisName] == singleTradingDays)
                ]['ReturnPercentage'].mean()
                heatmap1DataList[index1].append(round(meanValue, 2))

        if (heatmap1AnnotationValueSwitch):
            heatmap1Chart.add_heatmap(
                z=heatmap1DataList,
                colorscale=[[0, 'rgb(255, 0, 0)'], [0.5, 'rgb(255, 255, 255)'], [1, 'rgb(0, 255, 0)']],
                x=totalTradingDays, y=weekDays[::-1],
                zmid=0,
                text=heatmap1DataList, texttemplate='%{text}', textfont={'size': 12},
                hovertemplate='Average Return: %{z}%<br>       Weekday: %{y}<extra></extra>',
                hoverongaps=False
            )
        else:
            heatmap1Chart.add_heatmap(
                z=heatmap1DataList,
                colorscale=[[0, 'rgb(255, 0, 0)'], [0.5, 'rgb(255, 255, 255)'], [1, 'rgb(0, 255, 0)']],
                x=totalTradingDays, y=weekDays[::-1],
                zmid=0,
                text=heatmap1DataList,
                hovertemplate='Average Return: %{z}%<br>       Weekday: %{y}<extra></extra>',
                hoverongaps=False
            )

        heatmap1Chart.update_layout(
            title='Heatmap Daily Chart',
            xaxis_title=xAxisTitle,
            yaxis_title='Weekdays',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        
    """
        Walk Forward Superimposed Returns Chart for Daily only
    """

    if symbolNameToPlot not in walkForwardSuperimposedChartSymbol:
        walkForwardSuperimposedChartSymbol.insert(0, symbolNameToPlot)
    
    for walkForwardSymbol in walkForwardSuperimposedChartSymbol:   
        df_walkForward = pd.read_csv('./Symbols/' + walkForwardSymbol + '/1_Daily.csv')
        df_walkForward['Date'] = pd.to_datetime(df_walkForward['Date'], format='%Y-%m-%d')
        df_walkForward['ExpiryWeeklyDate'] = pd.to_datetime(df_walkForward['ExpiryWeeklyDate'], format='%Y-%m-%d')
        df_walkForward['MondayWeeklyDate'] = pd.to_datetime(df_walkForward['MondayWeeklyDate'], format='%Y-%m-%d')
        df_walkForward['Year'] = df_walkForward['Date'].dt.year
        df_walkForward = df_walkForward.dropna()
        # choose date range
        df_walkForward = df_walkForward[(df_walkForward['Date'] >= scannerStartDate) & (df_walkForward['Date'] <= scannerEndDate)]

        # choose even/odd years
        if (evenOddYearsValue != 'All'):
            df_walkForward = df_walkForward[df_walkForward['EvenYear'] == evenOddYearsValue]

        # choose specific month
        if (specificMonthValue != 0):
            df_walkForward = df_walkForward[df_walkForward['Date'].dt.month == specificMonthValue]

        # choose monday/expiry weeks
        if (specificExpiryWeekMonthlyValue != 0):
            df_walkForward = df_walkForward[df_walkForward['ExpiryWeekNumberMonthly'] == specificExpiryWeekMonthlyValue]
        if (specificMondayWeekMonthlyValue != 0):
            df_walkForward = df_walkForward[df_walkForward['MondayWeekNumberMonthly'] == specificMondayWeekMonthlyValue]
    
        if walkForwardSymbol in colorDict:
            lineColor = colorDict[walkForwardSymbol]
        else:
            lineColor = 'rgb' + str((random.randint(1, 265), random.randint(1, 256), random.randint(1, 256)))
            colorDict[walkForwardSymbol] = lineColor
        
        inTheSampleDataFrame = df_walkForward[(df_walkForward['Date'] >= inTheSampleDataRangeStartDate) & (df_walkForward['Date'] <= inTheSampleDataRangeEndDate)]
        outOfTheSampleDataFrame = df_walkForward[(df_walkForward['Date'] >= outOfTheSampleDataRangeStartDate) & (df_walkForward['Date'] <= outOfTheSampleDataRangeEndDate)]
        
        if ((len(inTheSampleDataFrame) > 0) and (len(outOfTheSampleDataFrame) > 0)):
            returnsAggregate = pd.DataFrame()
            hoverTextChange = ''

            if (walkForwardSuperimposedChartTypeValue == 'Weekday'):
                returnsAggregate = inTheSampleDataFrame.groupby(walkForwardSuperimposedChartTypeValue)['ReturnPercentage'].mean().reindex(weekDays).reset_index()
            else:
                returnsAggregate = inTheSampleDataFrame.groupby(walkForwardSuperimposedChartTypeValue)['ReturnPercentage'].mean().reset_index()

            if (walkForwardSuperimposedChartTypeValue == 'Weekday'):
                hoverTextChange = '  WTD '
            elif (walkForwardSuperimposedChartTypeValue == 'CalenderMonthDay' or walkForwardSuperimposedChartTypeValue == 'TradingMonthDay'):
                hoverTextChange = '  MTD '
            elif (walkForwardSuperimposedChartTypeValue == 'CalenderYearDay' or walkForwardSuperimposedChartTypeValue == 'TradingYearDay'):
                hoverTextChange = '  YTD '

            returnsList = ((returnsAggregate['ReturnPercentage']/100)+1).to_list()
            compoundedReturnsList = [0] * len(returnsList)
            compoundedReturnsList[0] = returnsList[0]

            for i in range(1, len(returnsList)):
                compoundedReturnsList[i] = compoundedReturnsList[i-1]*returnsList[i]

            returnsAggregate['SuperImposedReturn'] = compoundedReturnsList
            returnsAggregate['SuperImposedReturn'] = (returnsAggregate['SuperImposedReturn']-1)*100
            superImposedReturnList = returnsAggregate['SuperImposedReturn'].to_list()

            hoverExtraTextMessageSuperimposedChart = returnsAggregate['ReturnPercentage'].to_list()
            xAxisList = returnsAggregate[walkForwardSuperimposedChartTypeValue].to_list()

            hoverExtraTextMessageSuperimposedChart = [
                f'{(xAxisList[i]) if (walkForwardSymbol == walkForwardSuperimposedChartSymbol[0]) else ""}<br>' +
                f'{(walkForwardSymbol)}' + '<br>' +
                'In the Sample Returns' + '<br>' +
                hoverTextChange + 'Return: ' + f'{superImposedReturnList[i]:.2f}' + '%<br>' +
                'Daily Change: ' + f'{hoverExtraTextMessageSuperimposedChart[i]:.2f}' + '%'
                for i in range(len(hoverExtraTextMessageSuperimposedChart))
            ]

            walkForwardSuperimposedChart.add_scatter(
                x=returnsAggregate[walkForwardSuperimposedChartTypeValue],
                y=returnsAggregate['SuperImposedReturn'],
                text=hoverExtraTextMessageSuperimposedChart,
                hoverinfo='text', name=f'{walkForwardSymbol} (In the Sample)',
                line=dict(color=lineColor)
            )

        walkForwardSuperimposedChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        walkForwardSuperimposedChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        walkForwardSuperimposedChart.update_layout(
            title='Walk Forward Superimposed Daily Chart',
            xaxis_title='Days',
            yaxis_title='Compounded Percentage Return', yaxis_tickformat='.2f',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            ),
            legend=dict(
                x=0.02, y=0.99,
                xanchor='left', yanchor='top',
                traceorder='normal', bgcolor='rgba(0,0,0,0)'
            )
                )
    walkForwardSuperimposedChart.add_hline(y=0, line_width=2, line_dash='solid', line_color='grey')
    return [query1DataTableReturnPlot, heatmap1Chart, walkForwardSuperimposedChart]

@callback(
    Output(component_id='phenomenaBackTester_outputTable_download_csv', component_property='data'),
    Input('phenomenaBackTester_outputTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def phenomenaBackTester_outputTable_download_phenomenaBackTester(
    phenomenaBackTester_outputTable_download_button
):
    return phenomenaBackTestTradeListDownload


@callback(
    Output(component_id='phenomenaBackTester_reportTable_download_csv', component_property='data'),
    Input('phenomenaBackTester_reportTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def phenomenaBackTester_reportTable_download_phenomenaBackTester(
    phenomenaBackTester_reportTable_download_button
):
    return phenomenaBackTestReportDownload

@callback(
    Output(component_id='daily_query1DataTable_download_csv', component_property='data'),
    Input('daily_query1DataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def query1DataTable_download_daily(
    query1DataTable_download_button
):
    return query1DataTableDownload

