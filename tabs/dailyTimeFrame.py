from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
from itertools import zip_longest
import random


from helper import monthNames,monthDict,hoverElecList,lineStyleElecList,symbolNamesToDropdown, \
    watchListToDropDown, specialDaysToDropdown, monthFullNames, \
    tradingDays, calenderDays, colorDict, \
    getDataTableForPlot, getDataTableStatistics, getMonthNumber, getHistoricTrendingDays, \
    filterDataFrameFromHelper, getTrendingDays, \
    getRecentDayReturnPercentage, getRecentWeekReturnPercentage, getRecentMonthReturnPercentage,\
    getElectionfilterDataFrame,electionInfoDf,MaincolorDict,electionDateList,SecondaryColorList, weekDays


allDayDataTableDownload = pd.DataFrame()
dayDataTableDownload = pd.DataFrame()
specialDayDailyReturnsDataTableDownload = pd.DataFrame()
specialDayNthDayReturnsDataTableDownload = pd.DataFrame()
phenomenaDataTableDownload = pd.DataFrame()
dailyVsMonthlyDataTableDownload = pd.DataFrame()
dailyPnLDataTableDownload = pd.DataFrame()


dailyTimeFrameLayout = html.Div([

    html.Br(), html.Br(),

    # FILTERED Daily CHART INPUT
    html.H2('Filtered Daily Chart Inputs'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Symbol'), width=5, align='left'),
        dbc.Col(html.H6('Select Chart Scale Type'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_symbolNameToPlot',
                                   options=symbolNamesToDropdown,
                                   value='BANKNIFTY',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_chartScaleType',
                           inline=True,
                           options=[dict(label='Linear', value='linear'),
                                    dict(label='Log', value='log')],
                           value='linear',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Date Range(OR Last N Days)'), width=5, align='left'),
        dbc.Col(html.H6('Enter Last N Days Data(OR Date Range)'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.DatePickerRange(id='daily_dataRange',
                                min_date_allowed=date(1900, 1, 1), max_date_allowed=date(2025, 12, 31),
                                start_date=date(2016, 1, 1), end_date=date(2023, 12, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='daily_dateLastNDays',
                                type='number',
                                placeholder='Enter Zero(0) to Disable',
                                style={'width': '250px', 'height': '30px'},
                                min=0, step=1, value=0,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    # YEARLY FILTER
    html.H4('Yearly Filters', style={'color': '#00218fa1'}),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Positive/Negative Years'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd Years'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_positiveNegativeYears',
                           inline=True,
                           options=[dict(label='All Years', value='All'),
                                    dict(label='Positive Years only', value=True),
                                    dict(label='Negative Years only', value=False)
                                ],
                           
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_evenOddYears',
                           inline=True,
                           options=[dict(label='All Years', value='All'),
                                    dict(label='Even Years only', value = True),
                                    dict(label='Odd Years only', value = False),
                                ],

                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
    ]),
    html.Br(),html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Leap/Election Years'), width=5, align='left'),
        dbc.Col(html.H6('Select Decade Years'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_leapElectionYears',
                           inline=True,
                           options=[dict(label='All Years', value='All'),
                                    dict(label='Leap Years only', value = 'Leap Years'),
                                    dict(label='Election Years only', value = 'Election Years')    
                                ],

                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_decadeYears',
                                   options=[i for i in range(1, 11)],
                                   value=[i for i in range(1, 11)], multi=True,
                                   clearable=False, maxHeight=250,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=5, align='left'
        )
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    # MONTHLY FILTER
    html.H4('Monthly Filters', style={'color': '#00218fa1'}),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Positive/Negative Months'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd Months'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_positiveNegativeMonths',
                           inline=True,
                           options=[dict(label='All Months', value='All'),
                                    dict(label='Positive Months only', value=True),
                                    dict(label='Negative Months only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_evenOddMonths',
                           inline=True,
                           options=[dict(label='All Months', value='All'),
                                    dict(label='Even Months only', value=True),
                                    dict(label='Odd Months only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(),
    html.H6('Select Specific Month'),
    html.Div([
        dcc.Slider(id='daily_specificMonthSelection',
                   min=0, max=12, step=1,
                   marks={
                       0: {'label': 'Disable', 'style': {'color': 'black'}},
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
                   persistence=True, persistence_type='session')
    ], style=dict(width='60%')
    ),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    # EXPIRY WEEKLY FILTER
    html.H4('Expiry Weekly Filters', style={'color': '#00218fa1'}),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Positive/Negative Expiry Weeks'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd Expiry Weeks(Monthly Count)'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_positiveNegativeExpiryWeeks',
                           inline=True,
                           options=[
                                    dict(label='All Weeks', value='All'),
                                    dict(label='Positive Weeks only', value=True),
                                    dict(label='Negative Weeks only', value=False)
                                ],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_evenOddExpiryWeeksMonthly',
                           inline=True,
                           options= [
                                    dict(label='All Weeks', value='All'),
                                    dict(label='Even Weeks only', value=True),
                                    dict(label='Odd Weeks only', value=False)
                                ],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Specific Expiry Weeks(Monthly Count)'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd Expiry Weeks(Yearly Count)'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Slider(id='daily_specificExpiryWeekMonthlySelection',
                                 min=0, max=5, step=1,
                                 marks={
                                     0: {'label': 'Disable', 'style': {'color': 'black'}},
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
            dcc.RadioItems(id='daily_evenOddExpiryWeeksYearly',
                           inline=True,
                           options=[dict(label='All Weeks', value='All'),
                                    dict(label='Even Weeks only', value=True),
                                    dict(label='Odd Weeks only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    # MONDAY WEEKLY FILTER
    html.H4('Monday Weekly Filters', style={'color': '#00218fa1'}),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select Positive/Negative Monday Weeks'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd Monday Weeks(Monthly Count)'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_evenOddMondayWeeksMonthly',
                           inline=True,
                           options=[dict(label='All Weeks', value='All'),
                                    dict(label='Even Weeks only', value=True),
                                    dict(label='Odd Weeks only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_positiveNegativeMondayWeeks',
                           inline=True,
                           options=[dict(label='All Weeks', value='All'),
                                    dict(label='Positive Weeks only', value=True),
                                    dict(label='Negative Weeks only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Specific Monday Weeks(Monthly Count)'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd Monday Weeks(Yearly Count)'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Slider(id='daily_specificMondayWeekMonthlySelection',
                                 min=0, max=5, step=1,
                                 marks={
                                     0: {'label': 'Disable', 'style': {'color': 'black'}},
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
            dcc.RadioItems(id='daily_evenOddMondayWeeksYearly',
                           inline=True,
                           options=[dict(label='All Weeks', value='All'),
                                    dict(label='Even Weeks only', value=True),
                                    dict(label='Odd Weeks only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),


    # DAILY FILTERS
    html.H4('Daily Filters', style={'color': '#00218fa1'}),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select Positive/Negative Days'), width=5, align='left'),
        dbc.Col(html.H6('Select Week Days'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_positiveNegativeDays',
                           inline=True,
                           options=[dict(label='All Days', value='All'),
                                    dict(label='Positive Days only', value=True),
                                    dict(label='Negative Days only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.Checklist(id='daily_weekdayNames',
                          inline=True,
                          options=[dict(label='Monday', value='Monday'),
                                   dict(label='Tuesday', value='Tuesday'),
                                   dict(label='Wednesday', value='Wednesday'),
                                   dict(label='Thursday', value='Thursday'),
                                   dict(label='Friday', value='Friday')],
                          value=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                          className='checklist_group', inputClassName='checklist_input', labelClassName='checklist_label',
                          persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Even/Odd Calendar Days(Monthly Count)'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd Calendar Days(Yearly Count)'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_evenOddCalenderMonthDays',
                           inline=True,
                           options=[dict(label='All Days', value='All'),
                                    dict(label='Even Days only', value=True),
                                    dict(label='Odd Days only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_evenOddCalenderYearDays',
                           inline=True,
                           options=[dict(label='All Days', value='All'),
                                    dict(label='Even Days only', value=True),
                                    dict(label='Odd Days only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Even/Odd Trading Days(Monthly Count)'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd Trading Days(Yearly Count)'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_evenOddTradingMonthDays',
                           inline=True,
                           options=[dict(label='All Days', value='All'),
                                    dict(label='Even Days only', value=True),
                                    dict(label='Odd Days only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_evenOddTradingYearDays',
                           inline=True,
                           options=[dict(label='All Days', value='All'),
                                    dict(label='Even Days only', value=True),
                                    dict(label='Odd Days only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),


    # SELECT PERCENTAGE CHANGE
    html.H4('Select Percentage Change Range - To Remove Outliers', style={'color': '#00218fa1'}),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('For Daily'), width=5, align='left'),
        dbc.Col(html.H6('For Monday Weekly'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='daily_dailyPercentageChangeSwitch',  # type: ignore
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='daily_mondayWeeklyPercentageChangeSwitch',  # type: ignore
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        )
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.RangeSlider(id='daily_dailyPercentageChange',
                                      min=-5, max=5,
                                      marks={str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(-5, 6, 1)},
                                      dots=False, updatemode='drag', allowCross=False,
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      included=True, value=[-2, 2],
                                      persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.RangeSlider(id='daily_mondayWeeklyPercentageChange',
                                      min=-15, max=15,
                                      marks={str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(-15, 16, 3)},
                                      dots=False, updatemode='drag', allowCross=False,
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      value=[-6, 6],
                                      persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        )
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('For Expiry Weekly'), width=5, align='left'),
        dbc.Col(html.H6('For Monthly'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='daily_expiryWeeklyPercentageChangeSwitch',  # type: ignore
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='daily_monthlyPercentageChangeSwitch',  # type: ignore
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        )
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.RangeSlider(id='daily_expiryWeeklyPercentageChange',
                                      min=-15, max=15,
                                      marks={str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(-15, 16, 3)},
                                      dots=False, updatemode='drag', allowCross=False,
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      value=[-6, 6],
                                      persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.RangeSlider(id='daily_monthlyPercentageChange',
                                      min=-25, max=25,
                                      marks={str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(-25, 26, 5)},
                                      dots=False, updatemode='drag', allowCross=False,
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      value=[-10, 10],
                                      persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        )
    ]),

    html.Br(),
    dbc.Row([dbc.Col(html.H6('For Yearly'), width=5, align='left')]),
    dbc.Row([
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='daily_yearlyPercentageChangeSwitch',  # type: ignore
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        )
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.RangeSlider(id='daily_yearlyPercentageChange',
                                      min=-50, max=50,
                                      marks={str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(-50, 51, 10)},
                                      dots=False, updatemode='drag', allowCross=False,
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      value=[-20, 20],
                                      persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        )
    ]),

    html.Br(), html.Br(),


    # FILTERED DAILY CHART OUTPUT
    html.H2('Filtered Daily Chart Output'),
    dcc.Graph(id='daily_filteredChart', style=dict(height='90vh')),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),


    # YEARLY OVERLAY DAILY CHART OUTPUT
    html.H2('Yearly Overlay Daily Chart Inputs'),

    html.Br(),
    dbc.Row([dbc.Col(html.H6('Select Yearly Overlay Chart Type'), width=5, align='left'),
             dbc.Col(html.H6('Select Year Type'), width=5, align='left')]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_yearlyOverlayChartType',
                           inline=True,
                           options=[dict(label='Calendar Days', value='CalenderYearDay'),
                                    dict(label='Trading Days', value='TradingYearDay')],
                           value='CalenderYearDay',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_yearType',
                           inline=True,
                           options=[dict(label='All years', value='AllYears'),
                                    dict(label='Election Years', value='ElectionYears'),
                                    dict(label='Modi Years', value='ModiYears')],
                           value='AllYears',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    html.H2('Yearly Overlay Daily Chart Output'),
    dcc.Graph(id='daily_yearlyOverlayChart', style=dict(height='90vh')),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),


    # AGGREGATE DAILY CHART OUTPUT
    html.H2('Aggregate Daily Chart Inputs'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Field Name'), width=7, align='left'),
        dbc.Col(html.H6('Select Aggregate Type'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_aggregateChartFieldName',
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
            dcc.RadioItems(id='daily_aggregateChartType',
                           inline=True,
                           options=[dict(label='Total', value='total'),
                                    dict(label='Average', value='average'),
                                    dict(label='Maximum', value='maximum'),
                                    dict(label='Minimum', value='minimum')],
                           value='total',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(),
    html.H2('Aggregate Daily Chart Output'),
    dcc.Graph(id='daily_aggregateChart', style=dict(height='90vh')),

    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    # SUPERIMPOSED DAILY CHART INPUTS
    html.H2('Superimposed Daily Chart Inputs'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Superimposed Chart'), width=7, align='left'),
        dbc.Col(html.H6('Select Symbol '), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_superimposedChartType',
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
            html.Div([dcc.Dropdown(id='daily_superimposedSymbol',
                                   options=symbolNamesToDropdown,
                                   multi=True, value=[],
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=5, align='left'
        ),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Election Chart Type'), width=7, align='left'),
    ]),
    
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_superimposedElectionChartType',
                                   options=["All Years",
                                            "Election Years",
                                            "Pre Election Years",
                                            "Post Election Years",
                                            "Mid Election Years",
                                            "Current Year",
                                            "Modi Years"],
                                   multi=True, value=["All Years"],
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=7, align='left'
        ),
    ]),

    html.Br(), html.Br(),
    html.H2('Superimposed Daily Chart Output'),
    dcc.Graph(id='daily_superimposedChart', style=dict(height='90vh')),

    # DATA TABLES
    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Data Tables'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select DataTable Type'), width=7, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_dataTableType',
                           inline=True,
                           options=[dict(label='Calendar Year Days', value='CalenderYearDay'),
                                    dict(label='Trading Year Days', value='TradingYearDay'),
                                    dict(label='Calendar Month Days', value='CalenderMonthDay'),
                                    dict(label='Trading Month Days', value='TradingMonthDay'),
                                    dict(label='Weekdays', value='Weekday'),
                                    dict(label='All Months', value='MonthNumber'),
                                    dict(label='All Weeks', value='WeekNumber'),
                                    ],
                                    
                           value='CalenderMonthDay',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=7, align='left'
        )
    ]),

    html.Br(), html.Br(),
    dbc.Button(id='daily_allDayDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_allDayDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_allDayDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'index',
                                               },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold'
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
    dbc.Button(id='daily_typeDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_typeDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_typeDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           page_size=31,
                                           style_data_conditional=[
                                               {
                                                   'if': {
                                                       'column_id': 'index',
                                                   },
                                                   'backgroundColor': 'lightgrey',
                                                   'color': 'black',
                                                   'fontWeight': 'bold'
                                               },
                                               {
                                                   'if': {
                                                       'state': 'active'
                                                   },
                                                   'backgroundColor': 'lightgrey'
                                               },
                                               {
                                                   'if': {
                                                       'filter_query': '{Sum Return of All} > 0',
                                                       'column_id': 'Sum Return of All'
                                                   },
                                                   'backgroundColor': 'lightgreen'
                                               },
                                               {
                                                   'if': {
                                                       'filter_query': '{Sum Return of All} < 0',
                                                       'column_id': 'Sum Return of All'
                                                   },
                                                   'backgroundColor': 'indianred'
                                               }
                                           ],
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
                                           ))
                      ], style=dict(width='100%')),
            width=10, align='left'
        )
    ]),

    html.Br(), html.Br(),
    
    dbc.Row([
        dbc.Col(html.H6('Select Value To Plot'), width=4, align='left'),
        dbc.Col(html.H6('Select Value Type'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_valueToPlotOnBarGraph',
                           inline=True,
                           options=[dict(label='Average', value='Average'),
                                    dict(label='Sum', value='Sum')],
                           value='Average',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
         dbc.Col(
             dcc.RadioItems(id='daily_valueToPlotTypeForBarGraph',
                           inline=True,
                           options=[dict(label='Any', value='Any'),
                                    dict(label='Positive', value='Positive'),
                                    dict(label='Negative', value='Negative')
                                    ],
                           value='Positive',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        )
    ]),
    
    dcc.Graph(id='daily_typeDatatableBarGraph', style=dict(height='90vh')),
    dbc.Button(id='daily_typeDatatablePnL_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_typeDatatablePnL_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_typeDatatablePnL',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           page_size=31,
                                           style_data_conditional=[
                                               {
                                                   'if': {
                                                       'column_id': 'index',
                                                   },
                                                   'backgroundColor': 'lightgrey',
                                                   'color': 'black',
                                                   'fontWeight': 'bold'
                                               },
                                               {
                                                   'if': {
                                                       'state': 'active'
                                                   },
                                                   'backgroundColor': 'lightgrey'
                                               },
                                               {
                                                   'if': {
                                                       'filter_query': '{Sum Return of All} > 0',
                                                       'column_id': 'Sum Return of All'
                                                   },
                                                   'backgroundColor': 'lightgreen'
                                               },
                                               {
                                                   'if': {
                                                       'filter_query': '{Sum Return of All} < 0',
                                                       'column_id': 'Sum Return of All'
                                                   },
                                                   'backgroundColor': 'indianred'
                                               }
                                           ],
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
                                           ))
                      ], style=dict(width='100%')),
            width=10, align='left'
        )
    ]),
    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    # # SUPERIMPOSED RETURNS ON SPECIAL DAY
    html.H2('Superimposed Returns on Special Day'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Special Day'), width=4, align='left'),
        dbc.Col(html.H6('Select Range of Days'), width=7, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_specialDayToPlot',
                                   options=specialDaysToDropdown,
                                   value=specialDaysToDropdown[0],
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='daily_specialDayRangeOfDays',
                                 min=5, max=25, step=1,
                                 marks={i: {'label': str(i), 'style': {'color': 'black'}} for i in range(5, 26)},
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='top'),
                                 included=False,
                                 value=10,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=7, align='left'
        ),
    ]),

    html.Br(),
    html.H4('Superimposed Returns on Special Day Daily Chart', style={'color': '#00218fa1'}),
    dcc.Graph(id='daily_specialDayProbabilityChart', style=dict(height='90vh')),
    # DAILY RETURN TABLE
    html.Br(),
    html.H4('Daily Returns DataTable', style={'color': '#00218fa1'}),

    html.Br(),
    dbc.Button(id='daily_specialDayDailyReturnsDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_specialDayDailyReturnsDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_specialDayDailyReturnsDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'Date(T)',
                                               },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold',
                                               'minWidth': '100px'
                                           }],
                                           style_cell=dict(
                                               whiteSpace='pre-line'
                                           ),
                                           style_table={
                                               'overflowX': 'scroll'
                                           },
                                           style_header=dict(
                                               minWidth='70px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold'
                                           ),
                                           style_data=dict(
                                               minWidth='70px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='white', color='black'
                                           )),],
                     style=dict(width='100%')),
            width=24, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.H4('Returns from Nth Day(Before Special Day) DataTable', style={'color': '#00218fa1'}),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Nth Day'), width=7, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Slider(id='daily_specialDayNthDayReturns',
                                 min=1, max=10, step=1,
                                 marks={i: {'label': str(i), 'style': {'color': 'black'}} for i in range(1, 11)},
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='top'),
                                 included=False,
                                 value=3,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=7, align='left'
        ),
    ]),

    html.Br(),
    dbc.Button(id='daily_specialDayNthDayReturnsDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_specialDayNthDayReturnsDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_specialDayNthDayReturnsDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'Date(T-' + str(i) + ')',
                                               },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold',
                                               'minWidth': '100px'
                                           } for i in range(1, 11)],
                                           style_cell=dict(
                                               whiteSpace='pre-line'
                                           ),
                                           style_table={
                                               'overflowX': 'scroll'
                                           },
                                           style_header=dict(
                                               minWidth='70px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold'
                                           ),
                                           style_data=dict(
                                               minWidth='70px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='white', color='black'
                                           )),],
                     style=dict(width='100%')),
            width=24, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    # SEASONALITY PHENOMENA
    html.H2('Seasonality Phenomena'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Month'), width=3, align='left'),
        dbc.Col(html.H6('Select Phenomena Days'), width=9, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_phenomenaMonth',
                                   options=monthFullNames,
                                   value='April', multi=False,
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=3, align='left'
        ),
        dbc.Col(
            html.Div([dcc.RangeSlider(id='daily_phenomenaDays',
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
            width=9, align='left'
        )
    ]),

    dcc.Graph(id='daily_phenomenaChart', style=dict(height='90vh')),
    html.Br(),

    dbc.Button(id='daily_phenomenaDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_phenomenaDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_phenomenaDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'Years',
                                               },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold'
                                           }],
                                           style_cell=dict(
                                               whiteSpace='pre-line'
                                           ),
                                           style_header=dict(
                                               minWidth='70px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold'
                                           ),
                                           style_data=dict(
                                               minWidth='70px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='white', color='black'
                                           )),],
                     style=dict(width='100%')),
            width=3, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    html.H2('Monthly vs Yearly Returns'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Month'), width=3, align='left'),
        dbc.Col(html.H6('Select Phenomena Days'), width=9, align='left')
    ]),
     dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_monthlyVsYearlyMonthName',
                                   options = monthFullNames,
                                   value='January', multi=False,
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=3, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='daily_monthlyVsYearlyDays',
                                 min=1, max=10, step=1,
                                 marks={i: {'label': str(i), 'style': {'color': 'black'}} for i in range(1, 11)},
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='top'),
                                 included=False,
                                 value=5,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=7, align='left'
        ),
    ]),
    html.Br(),
    dbc.Button(id='daily_monthlyVsYearlyReturnsDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_monthlyVsYearlyReturnsDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_monthlyVsYearlyReturnsDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'Date(T-' + str(i) + ')',
                                               },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold',
                                               'minWidth': '100px'
                                           } for i in range(1, 11)],
                                           style_cell=dict(
                                               whiteSpace='pre-line'
                                           ),
                                           style_table={
                                               'overflowX': 'scroll'
                                           },
                                           style_header=dict(
                                               minWidth='70px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold'
                                           ),
                                           style_data=dict(
                                               minWidth='70px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='white', color='black'
                                           )),],
                     style=dict(width='100%')),
            width=24, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    # END-----------------

    # END-----------------

    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
],
    style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)



@callback(
    [
        Output(component_id='daily_filteredChart', component_property='figure'),
        Output(component_id='daily_yearlyOverlayChart', component_property='figure'),
        Output(component_id='daily_aggregateChart', component_property='figure'),
        Output(component_id='daily_superimposedChart', component_property='figure'),
        Output(component_id='daily_allDayDataTable', component_property='data'),
        Output(component_id='daily_typeDataTable', component_property='data'),
        Output(component_id='daily_specialDayProbabilityChart', component_property='figure'),
        Output(component_id='daily_specialDayDailyReturnsDataTable', component_property='data'),
        Output(component_id='daily_specialDayNthDayReturnsDataTable', component_property='data'),
        Output(component_id='daily_phenomenaChart', component_property='figure'),
        Output(component_id='daily_phenomenaDataTable', component_property='data'),
        Output(component_id='daily_typeDatatableBarGraph', component_property='figure'),
        Output(component_id='daily_typeDatatablePnL', component_property='data'),
    ],
    [
        Input('daily_symbolNameToPlot', 'value'), Input('daily_chartScaleType', 'value'),
        Input('daily_dataRange', 'start_date'), Input('daily_dataRange', 'end_date'), Input('daily_dateLastNDays', 'value'),
        Input('daily_positiveNegativeYears', 'value'), Input('daily_evenOddYears', 'value'),
        Input('daily_leapElectionYears', 'value'), Input('daily_decadeYears', 'value'),
        Input('daily_positiveNegativeMonths', 'value'), Input('daily_evenOddMonths', 'value'), Input('daily_specificMonthSelection', 'value'),
        Input('daily_positiveNegativeExpiryWeeks', 'value'), Input('daily_evenOddExpiryWeeksMonthly', 'value'),
        Input('daily_specificExpiryWeekMonthlySelection', 'value'), Input('daily_evenOddExpiryWeeksYearly', 'value'),
        Input('daily_positiveNegativeMondayWeeks', 'value'), Input('daily_evenOddMondayWeeksMonthly', 'value'),
        Input('daily_specificMondayWeekMonthlySelection', 'value'), Input('daily_evenOddMondayWeeksYearly', 'value'),
        Input('daily_positiveNegativeDays', 'value'), Input('daily_weekdayNames', 'value'),
        Input('daily_evenOddCalenderMonthDays', 'value'), Input('daily_evenOddCalenderYearDays', 'value'),
        Input('daily_evenOddTradingMonthDays', 'value'), Input('daily_evenOddTradingYearDays', 'value'),
        Input('daily_dailyPercentageChange', 'value'), Input('daily_dailyPercentageChangeSwitch', 'on'),
        Input('daily_mondayWeeklyPercentageChange', 'value'),  Input('daily_mondayWeeklyPercentageChangeSwitch', 'on'),
        Input('daily_expiryWeeklyPercentageChange', 'value'), Input('daily_expiryWeeklyPercentageChangeSwitch', 'on'),
        Input('daily_monthlyPercentageChange', 'value'), Input('daily_monthlyPercentageChangeSwitch', 'on'),
        Input('daily_yearlyPercentageChange', 'value'), Input('daily_yearlyPercentageChangeSwitch', 'on'),
        Input('daily_yearlyOverlayChartType', 'value'),Input('daily_yearType', 'value'),
        Input('daily_aggregateChartFieldName', 'value'), Input('daily_aggregateChartType', 'value'),
        Input('daily_superimposedChartType', 'value'),
        Input('daily_superimposedSymbol', 'value'),
        Input('daily_superimposedElectionChartType', 'value'),
        Input('daily_dataTableType', 'value'),
        Input('daily_specialDayToPlot', 'value'), Input('daily_specialDayRangeOfDays', 'value'), 
        Input('daily_specialDayNthDayReturns', 'value'),
        Input('daily_phenomenaMonth', 'value'), Input('daily_phenomenaDays', 'value'),
        Input('daily_valueToPlotOnBarGraph', 'value'), Input('daily_valueToPlotTypeForBarGraph', 'value'), 
    ]
)
def display_daily(
    symbolNameToPlotValue, chartScaleValue,
    startDate, endDate, dateLastNDaysValue,
    positiveNegativeYearFilter, evenOddYearFilter,
    leapElectionYearFilter, decadeYearsValue,
    positiveNegativeMonthFilter, evenOddMonthFilter, specificMonthSelectionValue,
    positiveNegativeExpiryWeekFilter, evenOddExpiryWeekMonthlyFilter,
    specificExpiryWeekMonthlySelectionValue, evenOddExpiryWeekYearlyFilter,
    positiveNegativeMondayWeekFilter, evenOddMondayWeekMonthlyFilter,
    specificMondayWeekMonthlySelectionValue, evenOddMondayWeekYearlyFilter,
    positiveNegativeDayFilter, weekdayNameFilter,
    evenOddCalenderMonthDayFilter, evenOddCalenderYearDayFilter,
    evenOddTradingMonthDayFilter, evenOddTradingYearDayFilter,
    dailyPercentageChangeFilter, dailyPercentageChangeFilterSwitch,
    mondayWeeklyPercentageChangeFilter, mondayWeeklyPercentageChangeFilterSwitch,
    expiryWeeklyPercentageChangeFilter, expiryWeeklyPercentageChangeFilterSwitch,
    monthlyPercentageChangeFilter, monthlyPercentageChangeFilterSwitch,
    yearlyPercentageChangeFilter, yearlyPercentageChangeFilterSwitch,
    yearlyOverlayChartTypeValue,YearlyNumberOfYearType,
    aggregateChartFieldNameValue, aggregateChartTypeValue,
    superimposedChartTypeValue, superimposedSymbol,
    superimposedElectionChartType,
    dataTableTypeValue,
    specialDayValue, specialDayRangeOfDaysValue, specialDayNthDayReturnsValues,
    phenomenaMonthValue, phenomenaDaysValue,
    valueToPlotOnBarGraph, valueToPlotTypeForBarGraph   
):

    df = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/1_Daily.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
    
    df['MonthNumber'] = df['Date'].dt.month
    df['WeekNumber'] = df['Date'].dt.strftime('%U').astype(int)
    df = df.dropna()
    
    # choose date range
    dateLastNDaysValue = dateLastNDaysValue if (type(dateLastNDaysValue) == int) else 0
    if (dateLastNDaysValue == 0):
        df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)]
    else:
        df = df.tail(dateLastNDaysValue)
    
    # choose positive/negative, even/odd years
    if (positiveNegativeYearFilter != 'All'):
        df = df[df['PositiveYear'] == positiveNegativeYearFilter]
    if (evenOddYearFilter != 'All'):
        df = df[df['EvenYear'] == evenOddYearFilter]

    # choose Leap/Election Years
    if (leapElectionYearFilter != 'All'):
        if leapElectionYearFilter == 'Election Years':
            df = df[df['Date'].dt.year.isin(electionDateList)]
        else:
            df = df[(df['Date'].dt.year % 4 == 0) & ((df['Date'].dt.year % 100 != 0) | (df['Date'].dt.year % 400 == 0))]


    # filter decade years
    decadeYearsValueNotPresent = [x for x in range(1, 11) if x not in decadeYearsValue]
    for decadeYearNotPresent in decadeYearsValueNotPresent:
        if (decadeYearNotPresent == 10):
            decadeYearNotPresent = 0
        df = df[(df['Date'].dt.year % 10) != decadeYearNotPresent]

    # choose positive/negative, even/odd months
    if (positiveNegativeMonthFilter != 'All'):
        df = df[df['PositiveMonth'] == positiveNegativeMonthFilter]
    if (evenOddMonthFilter != 'All'):
        df = df[df['EvenMonth'] == evenOddMonthFilter]
    if (specificMonthSelectionValue != 0):
        df = df[df['Date'].dt.month == specificMonthSelectionValue]

    # choose positive/negative, even/odd expiry weeks
    if (positiveNegativeExpiryWeekFilter != 'All'):
        df = df[df['PositiveExpiryWeek'] == positiveNegativeExpiryWeekFilter]
    if (evenOddExpiryWeekMonthlyFilter != 'All'):
        df = df[df['EvenExpiryWeekNumberMonthly'] == evenOddExpiryWeekMonthlyFilter]
    if ((specificExpiryWeekMonthlySelectionValue != 0) and (specificMonthSelectionValue != 0)):
        df = df[
            (df['ExpiryWeekNumberMonthly'] == specificExpiryWeekMonthlySelectionValue) &
            (df['ExpiryWeeklyDate'].dt.month == specificMonthSelectionValue)
        ]
    elif (specificExpiryWeekMonthlySelectionValue != 0):
        df = df[df['ExpiryWeekNumberMonthly'] == specificExpiryWeekMonthlySelectionValue]
    if (evenOddExpiryWeekYearlyFilter != 'All'):
        df = df[df['EvenExpiryWeekNumberYearly'] == evenOddExpiryWeekYearlyFilter]

    # choose positive/negative, even/odd monday weeks
    if (positiveNegativeMondayWeekFilter != 'All'):
        df = df[df['PositiveMondayWeek'] == positiveNegativeMondayWeekFilter]
    if (evenOddMondayWeekMonthlyFilter != 'All'):
        df = df[df['EvenMondayWeekNumberMonthly'] == evenOddMondayWeekMonthlyFilter]
    if ((specificMondayWeekMonthlySelectionValue != 0) and (specificMonthSelectionValue != 0)):
        df = df[
            (df['MondayWeekNumberMonthly'] == specificMondayWeekMonthlySelectionValue) &
            (df['MondayWeeklyDate'].dt.month == specificMonthSelectionValue)
        ]
    elif (specificMondayWeekMonthlySelectionValue != 0):
        df = df[df['MondayWeekNumberMonthly'] == specificMondayWeekMonthlySelectionValue]
    if (evenOddMondayWeekYearlyFilter != 'All'):
        df = df[df['EvenMondayWeekNumberYearly'] == evenOddMondayWeekYearlyFilter]

    # choose positive/negative, even/odd days
    if (positiveNegativeDayFilter != 'All'):
        df = df[df['PositiveDay'] == positiveNegativeDayFilter]
    if (len(weekdayNameFilter) > 0):
        df = df[df['Weekday'].isin(weekdayNameFilter)]
    if (evenOddCalenderMonthDayFilter != 'All'):
        df = df[df['EvenCalenderMonthDay'] == evenOddCalenderMonthDayFilter]
    if (evenOddCalenderYearDayFilter != 'All'):
        df = df[df['EvenCalenderYearDay'] == evenOddCalenderYearDayFilter]
    if (evenOddTradingMonthDayFilter != 'All'):
        df = df[df['EvenTradingMonthDay'] == evenOddTradingMonthDayFilter]
    if (evenOddTradingYearDayFilter != 'All'):
        df = df[df['EvenTradingYearDay'] == evenOddTradingYearDayFilter]

    # add more columns in dataframe
    df['Year'] = df['Date'].dt.year

    # outlier filters
    if (dailyPercentageChangeFilterSwitch):
        df = df[
            (df['ReturnPercentage'] >= dailyPercentageChangeFilter[0]) &
            (df['ReturnPercentage'] <= dailyPercentageChangeFilter[1])
        ]
    if (mondayWeeklyPercentageChangeFilterSwitch):
        df = df[
            (df['MondayWeeklyReturnPercentage'] >= mondayWeeklyPercentageChangeFilter[0]) &
            (df['MondayWeeklyReturnPercentage'] <= mondayWeeklyPercentageChangeFilter[1])
        ]
    if (expiryWeeklyPercentageChangeFilterSwitch):
        df = df[
            (df['ExpiryWeeklyReturnPercentage'] >= expiryWeeklyPercentageChangeFilter[0]) &
            (df['ExpiryWeeklyReturnPercentage'] <= expiryWeeklyPercentageChangeFilter[1])
        ]
    if (monthlyPercentageChangeFilterSwitch):
        df = df[
            (df['MonthlyReturnPercentage'] >= monthlyPercentageChangeFilter[0]) &
            (df['MonthlyReturnPercentage'] <= monthlyPercentageChangeFilter[1])
        ]
    if (yearlyPercentageChangeFilterSwitch):
        df = df[
            (df['YearlyReturnPercentage'] >= yearlyPercentageChangeFilter[0]) &
            (df['YearlyReturnPercentage'] <= yearlyPercentageChangeFilter[1])
        ]
    
    # all reuturn figures
    filteredChart = go.Figure()
    yearlyOverlayChart = go.Figure()
    aggregateChart = go.Figure()
    superimposedChart = go.Figure()
    specialDayProbabilityChart = go.Figure()
    phenomenaChart = go.Figure()
    daily_typeDatatableBarChart = go.Figure()

    # all return data tables
    allDayDataTable = pd.DataFrame()
    barGraphDataTable = pd.DataFrame()
    allDayDataTableReturnPlot = allDayDataTable.to_dict('records')
    dayDataTable = pd.DataFrame()
    dayDataTableReturnPlot = dayDataTable.to_dict('records')
    specialDayDailyReturnsDataTable = pd.DataFrame()
    specialDayDailyReturnsDataTableReturnPlot = specialDayDailyReturnsDataTable.to_dict('records')
    specialDayNthDayReturnsDataTable = pd.DataFrame()
    specialDayNthDayReturnsDataTableReturnPlot = specialDayNthDayReturnsDataTable.to_dict('records')
    phenomenaDataTable = pd.DataFrame(columns=['Years', 'Returns'], dtype=float)
    phenomenaDataTableReturnPlot = phenomenaDataTable.to_dict('records')
    dailyPnLDataTable = pd.DataFrame()
    dailyPnLDataTableReturnPlot = dailyPnLDataTable.to_dict('records')

    global allDayDataTableDownload
    global dayDataTableDownload
    global specialDayDailyReturnsDataTableDownload
    global specialDayNthDayReturnsDataTableDownload
    global phenomenaDataTableDownload
    global dailyPnLDataTableDownload   


    # plot chart only if data available after filters
    if (len(df) > 0):

        # create holidays date list only for daily time frame
        notAvailableDates = []
        notAvailableWeekEnds = ['sat', 'mon']

        tradingDates = df['Date'].to_list()
        startDateOfPlot = tradingDates[0]
        endDateOfPlot = tradingDates[len(tradingDates)-1]
        dateRangeStartToEnd = [
            startDateOfPlot+timedelta(days=x)for x in range((endDateOfPlot+timedelta(days=1)-startDateOfPlot).days)
        ]
        notAvailableDates = list((set(dateRangeStartToEnd) - set(tradingDates))) + list((set(tradingDates) - set(dateRangeStartToEnd)))

        """
            plot candle sticks filtered chart for daily only
        """

        returnPercentageList = df['ReturnPercentage'].to_list()
        returnPointsList = df['ReturnPoints'].to_list()
        hoverExtraTextMessageFilteredChart = [
            'change: ' + f'{returnPointsList[i]:.2f}' + ', ' + f'{returnPercentageList[i]:.2f}' + '%'
            for i in range(len(returnPercentageList))
        ]

        filteredChart.add_candlestick(
            x=df['Date'],
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            text=hoverExtraTextMessageFilteredChart
        )

        # update chart layout, axis and remove holidays from chart
        filteredChart.update_xaxes(
            rangeslider_visible=False,
            rangebreaks=[dict(values=notAvailableDates)],
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False,
            dtick = "M48" if evenOddYearFilter!=False else 'M36'    #To account for Odd Years Selection
        )
        filteredChart.update_yaxes(
            type=chartScaleValue,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        filteredChart.update_layout(
            title='Filtered Daily Chart',
            xaxis_title='Date', xaxis_tickformat='%d-%b(%a)<br>%Y',
            yaxis_title='Price', yaxis_tickformat='.0d',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        """
            yearly overlay chart for daily only
        """
        if YearlyNumberOfYearType == 'ElectionYears':
            allYearsListInData = sorted(list(set(df['Year']) & electionDateList))
        elif YearlyNumberOfYearType == 'ModiYears':
            allYearsListInData = sorted(list(set(df['Year']) & {2014,2019}))
        else:
            allYearsListInData = sorted(list(set(df['Year'])))
        
        
        for i in range(0, len(allYearsListInData)):
            yearRotationalData = df[df['Year'] == allYearsListInData[i]]
            yearlyOverlayChart.add_scatter(
                x=yearRotationalData[yearlyOverlayChartTypeValue],
                y=yearRotationalData['ReturnPercentage'],
                name=allYearsListInData[i]
            )

        yearlyOverlayChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        yearlyOverlayChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        yearlyOverlayChart.update_layout(
            title='Yearly Overlay Daily Chart',
            xaxis_title='Days', xaxis_tickformat='%d-%b(%a)<br>%Y',
            yaxis_title='Percentage Change', yaxis_tickformat='.2f',
            legend_title='Years',showlegend = True,
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        yearlyOverlayChart.add_hline(y=0, line_width=1, line_dash='solid', line_color='black')

        """
            aggregate chart for daily only
        """
        aggregateDataFrame = pd.DataFrame()

        if (aggregateChartTypeValue == 'total'):
            aggregateDataFrame = df.groupby(aggregateChartFieldNameValue)['ReturnPercentage'].sum().reset_index()
        elif (aggregateChartTypeValue == 'average'):
            aggregateDataFrame = df.groupby(aggregateChartFieldNameValue)['ReturnPercentage'].mean().reset_index()
        elif (aggregateChartTypeValue == 'maximum'):
            aggregateDataFrame = df.groupby(aggregateChartFieldNameValue)['ReturnPercentage'].max().reset_index()
        elif (aggregateChartTypeValue == 'minimum'):
            aggregateDataFrame = df.groupby(aggregateChartFieldNameValue)['ReturnPercentage'].min().reset_index()

        aggregateChart.add_bar(
            x=aggregateDataFrame[aggregateChartFieldNameValue],
            y=aggregateDataFrame['ReturnPercentage'],
            marker=dict(color=np.where(aggregateDataFrame['ReturnPercentage'] < 0, 'red', 'green'))
        )
        if (aggregateChartFieldNameValue == 'Weekday'):
            aggregateChart.update_xaxes(
                categoryorder='array',
                categoryarray=weekDays
            )
        aggregateChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        aggregateChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        aggregateChart.update_layout(
            title='Aggregate Daily Chart',
            xaxis_title='Days',
            yaxis_title='Percentage Change', yaxis_tickformat='.2f',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        aggregateChart.add_hline(y=0, line_width=1, line_dash='solid', line_color='grey')

        """
            super imposed chart for daily only
        """
        returnsAggregate = pd.DataFrame()
        electDataTableDf = pd.DataFrame()
        hoverTextChange = ''
        coloridx = 0

        if symbolNameToPlotValue not in superimposedSymbol:
            superimposedSymbol.insert(0, symbolNameToPlotValue)

        for symbolName in superimposedSymbol:
            if symbolName != symbolNameToPlotValue:
                elecDf = filterDataFrameFromHelper(symbolName, chartScaleValue, startDate, endDate, dateLastNDaysValue, positiveNegativeYearFilter, evenOddYearFilter, decadeYearsValue, positiveNegativeMonthFilter, evenOddMonthFilter, specificMonthSelectionValue, positiveNegativeExpiryWeekFilter, evenOddExpiryWeekMonthlyFilter, specificExpiryWeekMonthlySelectionValue, evenOddExpiryWeekYearlyFilter, positiveNegativeMondayWeekFilter, evenOddMondayWeekMonthlyFilter, specificMondayWeekMonthlySelectionValue, evenOddMondayWeekYearlyFilter,
                                    positiveNegativeDayFilter, weekdayNameFilter, evenOddCalenderMonthDayFilter, evenOddCalenderYearDayFilter, evenOddTradingMonthDayFilter, evenOddTradingYearDayFilter, dailyPercentageChangeFilter, dailyPercentageChangeFilterSwitch, mondayWeeklyPercentageChangeFilter, mondayWeeklyPercentageChangeFilterSwitch, expiryWeeklyPercentageChangeFilter, expiryWeeklyPercentageChangeFilterSwitch, monthlyPercentageChangeFilter, monthlyPercentageChangeFilterSwitch, yearlyPercentageChangeFilter, yearlyPercentageChangeFilterSwitch)
            else:
                elecDf = df.copy(deep=True)
            
            if len(superimposedElectionChartType) == 0:
                superimposedElectionChartType = ['All Years']
                
            if len(superimposedElectionChartType) > 0:
                
                for electionIdx in range(len(superimposedElectionChartType)):
                    if symbolNameToPlotValue == symbolName:
                        colorDict[symbolNameToPlotValue+superimposedElectionChartType[electionIdx]] = MaincolorDict[superimposedElectionChartType[electionIdx]]
                    else:
                        if coloridx < len(SecondaryColorList): 
                            lineColor = SecondaryColorList[coloridx]
                            coloridx += 1
                        else:
                            while(1):
                                lineColor = 'rgb' + str((random.randint(1, 265), random.randint(1, 256), random.randint(1, 256)))
                                if lineColor not in SecondaryColorList:
                                    SecondaryColorList.append(lineColor)
                                    break
                        colorDict[symbolName+superimposedElectionChartType[electionIdx]] = lineColor        

                    dataFrame = getElectionfilterDataFrame(superimposedElectionChartType[electionIdx],electionInfoDf,elecDf)

                    #For Plotting Data Table
                    if electionIdx == 0 and symbolName == symbolNameToPlotValue:
                        electDataTableDf = dataFrame.copy(deep=True)

                    if len(dataFrame) > 0 :
                        if (superimposedChartTypeValue == 'Weekday'):
                            returnsAggregate = dataFrame.groupby(superimposedChartTypeValue)['ReturnPercentage'].mean().reindex(weekDays).reset_index()
                        else:
                            returnsAggregate = dataFrame.groupby(superimposedChartTypeValue)['ReturnPercentage'].mean().reset_index()
                        
                        if (superimposedChartTypeValue == 'Weekday'):
                            hoverTextChange = '  WTD '
                        elif (superimposedChartTypeValue == 'CalenderMonthDay' or superimposedChartTypeValue == 'TradingMonthDay'):
                            hoverTextChange = '  MTD '
                        elif (superimposedChartTypeValue == 'CalenderYearDay' or superimposedChartTypeValue == 'TradingYearDay'):
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
                        xAxisList = returnsAggregate[superimposedChartTypeValue].to_list()
                       
                        hoverExtraTextMessageSuperimposedChart = [
                            f'<b>{(xAxisList[i]) if (symbolName == superimposedSymbol[0] and electionIdx == 0) else ""}</b><br>' +
                            f'{(symbolName)}' + hoverElecList[superimposedElectionChartType[electionIdx]] + '<br>' +
                            hoverTextChange + 'Return: ' + f'{superImposedReturnList[i]:.2f}' + '%<br>' +
                            'Daily Change: ' + f'{hoverExtraTextMessageSuperimposedChart[i]:.2f}' + '%'
                            for i in range(len(hoverExtraTextMessageSuperimposedChart))
                        ]
                        superimposedChart.add_scatter(
                            x=xAxisList,
                            y=returnsAggregate['SuperImposedReturn'],
                            text=hoverExtraTextMessageSuperimposedChart,
                            hoverinfo='text',
                            name=symbolName + hoverElecList[superimposedElectionChartType[electionIdx]] ,
                            line=dict(
                                color=colorDict[symbolName+superimposedElectionChartType[electionIdx]],
                                dash = lineStyleElecList[superimposedElectionChartType[electionIdx]]
                            ),
                        )

        superimposedChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False,
        )
        superimposedChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        superimposedChart.update_layout(
            title='<b>Superimposed Daily Chart</b>',
            xaxis_title='<b>Days</b>',
            yaxis_title='<b>Compounded Percentage Return</b>', yaxis_tickformat='.2f',
            hovermode='x unified', hoverdistance=100,showlegend = True,
            font=dict(
                family='Arial Black',
                size=18,
                color='black'  
            ),
            xaxis=dict(
                tickfont=dict(
                    family='Arial Black',
                    size=20,  
                    color='black',
                )
            ),
            yaxis=dict(
               tickfont=dict(
                    family='Arial Black',
                    size=20,  
                    color='black',
                )
            ),
            legend=dict(
                itemclick='toggleothers',
                font=dict(
                    family='Arial Black',
                    size=18,  
                    color='black',
                )
            ),
        )
        superimposedChart.add_hline(y=0, line_width=2, line_dash='solid', line_color='grey')

        """
            dataTable calculation
        """
        try:
            allDayReturnPoints = np.array(electDataTableDf['ReturnPercentage'].to_list())

            allDaysStats = getDataTableStatistics(allDayReturnPoints)
            allDayDataTable = pd.concat([allDayDataTable, allDaysStats], axis=1)
            allDayDataTable.columns = ['All Days']
            allDayDataTableReturnValue = getDataTableForPlot(allDayDataTable)
            allDayDataTableReturnPlot = allDayDataTableReturnValue[0]
            allDayDataTableDownload = dcc.send_data_frame(allDayDataTableReturnValue[1].to_csv, 'Youngturtle_All_Days.csv')

            dataTableColumns = []
            if (dataTableTypeValue == 'Weekday'):
                dataTableColumns = weekDays
            else:
                dataTableColumns.extend(range(int(min(electDataTableDf[dataTableTypeValue])), int(max(electDataTableDf[dataTableTypeValue])+1), 1))

            for dayName in dataTableColumns:
                dayReturnPoints = np.array(electDataTableDf[electDataTableDf[dataTableTypeValue] == dayName]['ReturnPercentage'].to_list())
                dayStats = getDataTableStatistics(dayReturnPoints)
                dayDataTable = pd.concat([dayDataTable, dayStats], axis=1)
            
            dayDataTable.columns = dataTableColumns
            dayDataTableReturnValue = getDataTableForPlot(dayDataTable)
            dayDataTableReturnPlot = dayDataTableReturnValue[0]
            barGraphDataTable = dayDataTableReturnValue[1].copy(deep=True)
            dayDataTableDownload = dcc.send_data_frame(dayDataTableReturnValue[1].to_csv, 'Youngturtle_Individual_Days.csv')
        except:
            print("ERROR IN DATA TABLE")


        """
            special day charts for daily only
        """
        dfForSpecialDayProbabilityChart = df.copy(deep=True)
        dfForSpecialDayProbabilityChart = dfForSpecialDayProbabilityChart.dropna().reset_index().drop('index', axis=1)
        specialDayDates = pd.read_csv('./SpecialDays/SpecialDays.csv').apply(pd.to_datetime, format='%d-%m-%Y', axis=1)
        specialDayDates.columns = specialDaysToDropdown

        zerosList = [0.0]*specialDayRangeOfDaysValue
        oldestDate = dfForSpecialDayProbabilityChart['Date'][0]
        earliestDate = dfForSpecialDayProbabilityChart['Date'][len(dfForSpecialDayProbabilityChart)-1]

        allReturnsColumns = [
            *['Date(T)'],
            *[str('T-'+str(i)) for i in range(specialDayRangeOfDaysValue, 0, -1)],
            *['T'],
            *[str('T+'+str(i)) for i in range(1, specialDayRangeOfDaysValue+1)]
        ]

        allReturns = pd.DataFrame(columns=allReturnsColumns)
        selectedSpecialDates = [i for i in specialDayDates[specialDayValue] if ((i > oldestDate) & (i < earliestDate) 
                                                                                & (pd.to_datetime(i, format='%Y-%m-%d').year in list(df['Date'].dt.year.unique()))  #Added to filter out based on oddEvenYearFilter
                                )]
        
        for i, specialDate in enumerate(selectedSpecialDates):

            try:
                beforeReturns, afterReturns = [], []

                specialDayReturns = dfForSpecialDayProbabilityChart[(dfForSpecialDayProbabilityChart['Date'] == selectedSpecialDates[i])]['ReturnPercentage'].to_list()
                if (len(specialDayReturns) == 0):
                    specialDayReturns = [0.0]

                if (i == 0):
                    beforeReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] < selectedSpecialDates[i])
                    ]['ReturnPercentage'][-specialDayRangeOfDaysValue:].to_list()
                    afterReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] > selectedSpecialDates[i]) & (dfForSpecialDayProbabilityChart['Date'] < selectedSpecialDates[i+1])
                    ]['ReturnPercentage'][0:specialDayRangeOfDaysValue].to_list()

                elif (i+1 == len(selectedSpecialDates)):
                    beforeReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] < selectedSpecialDates[i]) & ((dfForSpecialDayProbabilityChart['Date'] > selectedSpecialDates[i-1]))
                    ]['ReturnPercentage'][-specialDayRangeOfDaysValue:].to_list()
                    afterReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] > selectedSpecialDates[i])
                    ]['ReturnPercentage'][0:specialDayRangeOfDaysValue].to_list()

                else:
                    beforeReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] < selectedSpecialDates[i]) & ((dfForSpecialDayProbabilityChart['Date'] > selectedSpecialDates[i-1]))
                    ]['ReturnPercentage'][-specialDayRangeOfDaysValue:].to_list()
                    afterReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] > selectedSpecialDates[i]) & (dfForSpecialDayProbabilityChart['Date'] < selectedSpecialDates[i+1])
                    ]['ReturnPercentage'][0:specialDayRangeOfDaysValue].to_list()

                returnsColumn = [
                    *[specialDate],
                    *[x+y for x, y in zip_longest(reversed(beforeReturns), reversed(zerosList), fillvalue=0)][::-1],
                    *specialDayReturns,
                    *[x+y for x, y in zip_longest(afterReturns, zerosList, fillvalue=0)]
                ]

                allReturns = pd.concat([
                    allReturns,
                    pd.DataFrame({value: [returnsColumn[i]] for i, value in enumerate(allReturnsColumns)})
                ])

            except IndexError:
                print('Error in selectedSpecialDates for loop')

        totalCount = [allReturns[colName][allReturns[colName] != 0].count() for colName in allReturnsColumns[1:]]
        averageReturns = [round(i, 2) for i in allReturns[allReturnsColumns[1:]].mean()]
        totalSum = [round(allReturns[colName][allReturns[colName] != 0].sum(), 2) for colName in allReturnsColumns[1:]]

        positiveCount = [allReturns[colName][allReturns[colName] > 0].count() for colName in allReturnsColumns[1:]]
        positiveMean = [round(allReturns[colName][allReturns[colName] > 0].mean(), 2) for colName in allReturnsColumns[1:]]
        positiveSum = [round(allReturns[colName][allReturns[colName] > 0].sum(), 2) for colName in allReturnsColumns[1:]]

        negativeCount = [allReturns[colName][allReturns[colName] < 0].count() for colName in allReturnsColumns[1:]]
        negativeMean = [round(allReturns[colName][allReturns[colName] < 0].mean(), 2) for colName in allReturnsColumns[1:]]
        negativeSum = [round(allReturns[colName][allReturns[colName] < 0].sum(), 2) for colName in allReturnsColumns[1:]]

        superimposedReturns = [(i/100)+1 for i in averageReturns]

        for i in range(0, specialDayRangeOfDaysValue+1):
            if (i == 0):
                superimposedReturns[specialDayRangeOfDaysValue] = superimposedReturns[specialDayRangeOfDaysValue]
            else:
                superimposedReturns[specialDayRangeOfDaysValue-i] = (
                    superimposedReturns[specialDayRangeOfDaysValue-i]*superimposedReturns[specialDayRangeOfDaysValue-i+1]
                )
                superimposedReturns[specialDayRangeOfDaysValue+i] = (
                    superimposedReturns[specialDayRangeOfDaysValue+i]*superimposedReturns[specialDayRangeOfDaysValue+i-1]
                )

        try:
            superimposedReturns = [round((i-1)*100, 2) for i in superimposedReturns]
            allReturns['Date(T)'] = allReturns['Date(T)'].dt.strftime('%d-%m-%Y')
        except AttributeError:
            print('Error in date type cast of selectedSpecialDates super imposed returns')

        allReturns = pd.concat([
            allReturns,
            pd.DataFrame({value: [[*['All Count'], *totalCount][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        allReturns = pd.concat([
            allReturns,
            pd.DataFrame({value: [[*['Positive Count'], *positiveCount][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        allReturns = pd.concat([
            allReturns,
            pd.DataFrame({value: [[*['Negative Count'], *negativeCount][i]] for i, value in enumerate(allReturnsColumns)})
        ])

        allReturns = pd.concat([
            allReturns,
            pd.DataFrame({value: [[*['Average Return of All'], *averageReturns][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        allReturns = pd.concat([
            allReturns,
            pd.DataFrame({value: [[*['Average Return of Positive'], *positiveMean][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        allReturns = pd.concat([
            allReturns,
            pd.DataFrame({value: [[*['Average Return of Negative'], *negativeMean][i]] for i, value in enumerate(allReturnsColumns)})
        ])

        allReturns = pd.concat([
            allReturns,
            pd.DataFrame({value: [[*['Sum Return of All'], *totalSum][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        allReturns = pd.concat([
            allReturns,
            pd.DataFrame({value: [[*['Sum Return of Positive'], *positiveSum][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        allReturns = pd.concat([
            allReturns,
            pd.DataFrame({value: [[*['Sum Return of Negative'], *negativeSum][i]] for i, value in enumerate(allReturnsColumns)})
        ])

        allReturns = pd.concat([
            allReturns,
            pd.DataFrame({value: [[*['Superimposed Returns'], *superimposedReturns][i]] for i, value in enumerate(allReturnsColumns)})
        ])

        allReturns = allReturns.fillna(0)

        specialDayProbabilityChart.add_scatter(
            x=allReturnsColumns[1:],
            y=superimposedReturns,
            line=dict(color='black')
        )
        specialDayProbabilityChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        specialDayProbabilityChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        specialDayProbabilityChart.update_layout(
            title='Superimposed Returns on Special Day Daily Chart',
            xaxis_title='Days',
            yaxis_title='Compounded Percentage Return', yaxis_tickformat='.2f',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        specialDayProbabilityChart.add_hline(y=0, line_width=2, line_dash='solid', line_color='grey')
        specialDayProbabilityChart.add_vline(x='T', line_width=2, line_dash='solid', line_color='grey')

        specialDayDailyReturnsDataTableReturnPlot = allReturns.to_dict('records')
        specialDayDailyReturnsDataTableDownload = dcc.send_data_frame(allReturns.set_index('Date(T)').to_csv, 'Youngturtle_SpecialDayDailyReturns.csv')

        """
            Returns from Nth Day(Before Special Day) DataTable
        """
        allReturnsColumns = [
            *['T'+str(i) for i in range(-(specialDayNthDayReturnsValues-1), 0)],
            *['T'],
            *['T+'+str(i) for i in range(1, specialDayRangeOfDaysValue+1)]
        ]

        allReturnsColumns = [*['Date(T-'+str(specialDayNthDayReturnsValues)+')'], *allReturnsColumns]
        nThDayBeforeSpecialDayClosePrices = pd.DataFrame(columns=allReturnsColumns)

        # nThDayBeforeSpecialDayClosePrices[allReturnsColumns[0]] = pd.to_datetime(nThDayBeforeSpecialDayClosePrices[allReturnsColumns[0]], format="%Y-%m-%d")
        # nThDayBeforeSpecialDayClosePrices[allReturnsColumns[1:]] = nThDayBeforeSpecialDayClosePrices[allReturnsColumns[1:]].astype(float)

        for i, specialDate in enumerate(selectedSpecialDates):
            try:
                specialDayReturns = dfForSpecialDayProbabilityChart[(dfForSpecialDayProbabilityChart['Date'] == selectedSpecialDates[i])][['Date', 'Close']]
                specialDayReturnsTemp = pd.DataFrame(pd.Series({'Date': selectedSpecialDates[i], 'Close': 0.0})).T
                if (len(specialDayReturns) == 0):
                    specialDayReturns = specialDayReturnsTemp.copy(deep=True)

                if (i == 0):
                    beforeReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] < selectedSpecialDates[i])
                    ][['Date', 'Close']][-specialDayNthDayReturnsValues:]
                    afterReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] > selectedSpecialDates[i]) & (dfForSpecialDayProbabilityChart['Date'] < selectedSpecialDates[i+1])
                    ][['Date', 'Close']][0:specialDayRangeOfDaysValue]

                elif (i+1 == len(selectedSpecialDates)):
                    beforeReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] < selectedSpecialDates[i]) & ((dfForSpecialDayProbabilityChart['Date'] > selectedSpecialDates[i-1]))
                    ][['Date', 'Close']][-specialDayNthDayReturnsValues:]
                    afterReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] > selectedSpecialDates[i])
                    ][['Date', 'Close']][0:specialDayRangeOfDaysValue]

                else:
                    beforeReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] < selectedSpecialDates[i]) & ((dfForSpecialDayProbabilityChart['Date'] > selectedSpecialDates[i-1]))
                    ][['Date', 'Close']][-specialDayNthDayReturnsValues:]
                    afterReturns = dfForSpecialDayProbabilityChart[
                        (dfForSpecialDayProbabilityChart['Date'] > selectedSpecialDates[i]) & (dfForSpecialDayProbabilityChart['Date'] < selectedSpecialDates[i+1])
                    ][['Date', 'Close']][0:specialDayRangeOfDaysValue]

                if (len(beforeReturns) < specialDayNthDayReturnsValues):
                    continue

                tempDataFrame = pd.concat([beforeReturns, specialDayReturns, afterReturns])
                nThDayDate, nThDayClose = tempDataFrame.iloc[0]
                nextCumulativePercentageChange = [
                    None if j == 0.0 else round(((j-nThDayClose)/nThDayClose)*100, 2) for j in tempDataFrame['Close'][1:]
                ]
                customRow = [*[nThDayDate], *nextCumulativePercentageChange]

                if (len(customRow) > 0):
                    try:
                        nThDayBeforeSpecialDayClosePrices = pd.concat([
                            nThDayBeforeSpecialDayClosePrices,
                            pd.DataFrame({value: [customRow[j]] for j, value in enumerate(allReturnsColumns)})
                        ])

                    except IndexError:
                        print('Error in Nth day before Special day Loop')

                    # print(nThDayBeforeSpecialDayClosePrices.dtypes)
            except IndexError:
                print('Error in selectedSpecialDates for loop')

        if (specialDayNthDayReturnsValues > 1):
            nThDayBeforeSpecialDayClosePrices = nThDayBeforeSpecialDayClosePrices.ffill(axis=1)
        else:
            nThDayBeforeSpecialDayClosePrices = nThDayBeforeSpecialDayClosePrices.ffill()

        if (len(nThDayBeforeSpecialDayClosePrices) > 0):
            try:
                totalCount = [nThDayBeforeSpecialDayClosePrices[colName][nThDayBeforeSpecialDayClosePrices[colName] != 0].count() for colName in allReturnsColumns[1:]]
                averageReturns = [round(i, 2) for i in nThDayBeforeSpecialDayClosePrices[allReturnsColumns[1:]].mean()]
                totalSum = [round(nThDayBeforeSpecialDayClosePrices[colName][nThDayBeforeSpecialDayClosePrices[colName] != 0].sum(), 2) for colName in allReturnsColumns[1:]]

                positiveCount = [nThDayBeforeSpecialDayClosePrices[colName][nThDayBeforeSpecialDayClosePrices[colName] > 0].count() for colName in allReturnsColumns[1:]]
                positiveMean = [round(nThDayBeforeSpecialDayClosePrices[colName][nThDayBeforeSpecialDayClosePrices[colName] > 0].mean(), 2) for colName in allReturnsColumns[1:]]
                positiveSum = [round(nThDayBeforeSpecialDayClosePrices[colName][nThDayBeforeSpecialDayClosePrices[colName] > 0].sum(), 2) for colName in allReturnsColumns[1:]]

                negativeCount = [nThDayBeforeSpecialDayClosePrices[colName][nThDayBeforeSpecialDayClosePrices[colName] < 0].count() for colName in allReturnsColumns[1:]]
                negativeMean = [round(nThDayBeforeSpecialDayClosePrices[colName][nThDayBeforeSpecialDayClosePrices[colName] < 0].mean(), 2) for colName in allReturnsColumns[1:]]
                negativeSum = [round(nThDayBeforeSpecialDayClosePrices[colName][nThDayBeforeSpecialDayClosePrices[colName] < 0].sum(), 2) for colName in allReturnsColumns[1:]]

                nThDayBeforeSpecialDayClosePrices[allReturnsColumns[0]] = pd.to_datetime(nThDayBeforeSpecialDayClosePrices[allReturnsColumns[0]])
                nThDayBeforeSpecialDayClosePrices[allReturnsColumns[0]] = nThDayBeforeSpecialDayClosePrices[allReturnsColumns[0]].dt.strftime('%d-%m-%Y')
                nThDayBeforeSpecialDayClosePrices = pd.concat([
                    nThDayBeforeSpecialDayClosePrices,
                    pd.DataFrame({value: [[*['All Count'], *totalCount][i]] for i, value in enumerate(allReturnsColumns)})
                ])
                nThDayBeforeSpecialDayClosePrices = pd.concat([
                    nThDayBeforeSpecialDayClosePrices,
                    pd.DataFrame({value: [[*['Positive Count'], *positiveCount][i]] for i, value in enumerate(allReturnsColumns)})
                ])
                nThDayBeforeSpecialDayClosePrices = pd.concat([
                    nThDayBeforeSpecialDayClosePrices,
                    pd.DataFrame({value: [[*['Negative Count'], *negativeCount][i]] for i, value in enumerate(allReturnsColumns)})
                ])

                nThDayBeforeSpecialDayClosePrices = pd.concat([
                    nThDayBeforeSpecialDayClosePrices,
                    pd.DataFrame({value: [[*['Average Return of All'], *averageReturns][i]] for i, value in enumerate(allReturnsColumns)})
                ])
                nThDayBeforeSpecialDayClosePrices = pd.concat([
                    nThDayBeforeSpecialDayClosePrices,
                    pd.DataFrame({value: [[*['Average Return of Positive'], *positiveMean][i]] for i, value in enumerate(allReturnsColumns)})
                ])
                nThDayBeforeSpecialDayClosePrices = pd.concat([
                    nThDayBeforeSpecialDayClosePrices,
                    pd.DataFrame({value: [[*['Average Return of Negative'], *negativeMean][i]] for i, value in enumerate(allReturnsColumns)})
                ])

                nThDayBeforeSpecialDayClosePrices = pd.concat([
                    nThDayBeforeSpecialDayClosePrices,
                    pd.DataFrame({value: [[*['Sum Return of All'], *totalSum][i]] for i, value in enumerate(allReturnsColumns)})
                ])
                nThDayBeforeSpecialDayClosePrices = pd.concat([
                    nThDayBeforeSpecialDayClosePrices,
                    pd.DataFrame({value: [[*['Sum Return of Positive'], *positiveSum][i]] for i, value in enumerate(allReturnsColumns)})
                ])
                nThDayBeforeSpecialDayClosePrices = pd.concat([
                    nThDayBeforeSpecialDayClosePrices,
                    pd.DataFrame({value: [[*['Sum Return of Negative'], *negativeSum][i]] for i, value in enumerate(allReturnsColumns)})
                ])

                nThDayBeforeSpecialDayClosePrices = nThDayBeforeSpecialDayClosePrices.fillna(0)
                specialDayNthDayReturnsDataTableReturnPlot = nThDayBeforeSpecialDayClosePrices.to_dict('records')
                specialDayNthDayReturnsDataTableDownload = dcc.send_data_frame(nThDayBeforeSpecialDayClosePrices.set_index(allReturnsColumns[0]).to_csv, 'Youngturtle_SpecialDayNthDayReturns.csv')
            except AttributeError:
                print('Error in Nth day before Special day')

            """
                Seasonality Phenomena Calculations
            """
            phenomenaMonthValue = getMonthNumber(phenomenaMonthValue)
            phenomenaDaysValueStart, phenomenaDaysValueEnd = phenomenaDaysValue[0], phenomenaDaysValue[1]
            phenomenaGetMonthMultipier = 1 if phenomenaDaysValueStart < 0 else -1
            phenomenaGetMonthFilter = 1 if ((phenomenaDaysValueStart < 0) & (phenomenaMonthValue == 12)) else 12 if ((phenomenaDaysValueStart > 0) & (phenomenaMonthValue == 1)) else phenomenaMonthValue+(1*phenomenaGetMonthMultipier)
            requiredDataForPhenomena = pd.DataFrame()

            if (phenomenaDaysValueEnd > 0):

                requiredDataForPhenomena = df[
                    (df['Date'].dt.month == phenomenaMonthValue) |
                    (df['Date'].dt.month == phenomenaGetMonthFilter)
                ]
                lastTradingMonthDays = requiredDataForPhenomena[
                    requiredDataForPhenomena['Date'].dt.month != requiredDataForPhenomena['Date'].shift(-1).dt.month
                ]['Date'].to_list()

                for lastTradingMonthDay in lastTradingMonthDays:
                    tempDataframe = pd.DataFrame()
                    tempYear = lastTradingMonthDay.year
                    tempStartClosing, tempEndClosing = 0, 0
                    if (phenomenaDaysValueStart < 0):
                        if (lastTradingMonthDay.month != phenomenaMonthValue):
                            continue
                        tempDataframe = pd.concat([
                            requiredDataForPhenomena[requiredDataForPhenomena['Date'] <= lastTradingMonthDay][phenomenaDaysValueStart:],
                            requiredDataForPhenomena[requiredDataForPhenomena['Date'] > lastTradingMonthDay][0:phenomenaDaysValueEnd]
                        ])
                    else:
                        if (lastTradingMonthDay.month == phenomenaMonthValue):
                            continue
                        tempDataframe = requiredDataForPhenomena[requiredDataForPhenomena['Date'] > lastTradingMonthDay][phenomenaDaysValueStart-1:phenomenaDaysValueEnd]

                    if (len(tempDataframe) < 1):
                        continue
                    try:
                        tempStartClosing, tempEndClosing = tempDataframe['Close'].iloc[0], tempDataframe['Close'].iloc[-1]
                        percentageChange = round(((tempEndClosing/tempStartClosing)-1)*100, 2)

                        phenomenaDataTable = pd.concat([
                            phenomenaDataTable,
                            pd.DataFrame({'Years': [tempYear], 'Returns': [percentageChange]})
                        ])
                    except IndexError:
                        print('Error inside Phenomena Calculation Loop')

            phenomenaChart.add_scatter(
                x=phenomenaDataTable['Years'],
                y=phenomenaDataTable['Returns'],
                line=dict(color='black')
            )
            phenomenaChart.update_xaxes(
                rangeslider_visible=False,
                showline=True, linewidth=1, linecolor='grey',
                gridcolor='grey', griddash='dot',
                showspikes=True, spikemode='across', spikesnap='cursor',
                spikecolor='grey', spikethickness=1, spikedash='dash',
                fixedrange=False
            )
            phenomenaChart.update_yaxes(
                showline=True, linewidth=1, linecolor='grey',
                gridcolor='grey', griddash='dot',
                showspikes=True, spikemode='across', spikesnap='cursor',
                spikecolor='grey', spikethickness=1, spikedash='dash',
                fixedrange=False
            )
            phenomenaChart.update_layout(
                title='Phenomena Daily Chart',
                xaxis_title='Years', xaxis_tickformat='d',
                yaxis_title='Percentage Return', yaxis_tickformat='.2f',
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
            phenomenaChart.add_hline(y=0, line_width=2, line_dash='solid', line_color='grey')

            phenomenaDataTableReturnPlot = phenomenaDataTable.to_dict('records')
            phenomenaDataTableDownload = dcc.send_data_frame(phenomenaDataTable.set_index('Years').to_csv, 'Youngturtle_PhenomenaReturns.csv')
            """
                Bar Graph Calculations
            """
            filtered_columns = barGraphDataTable.columns
            if(len(barGraphDataTable)>0):
                barGraphDataTable['index'] = [i+1 for i in range(0, len(barGraphDataTable))]
                if(valueToPlotTypeForBarGraph!='Any'):
                    filtered_columns = [col for col in barGraphDataTable.columns if valueToPlotTypeForBarGraph in col]
                    filtered_columns = [col for col in filtered_columns if valueToPlotOnBarGraph in col]
                else:
                    valueToPlotTypeForBarGraph = 'All'
                    filtered_columns = [col for col in filtered_columns if valueToPlotOnBarGraph in col]
                    filtered_columns = [filtered_columns[0]]
                
                daily_typeDatatableBarChart = go.Figure(data=[go.Bar(x=barGraphDataTable['index'], y=barGraphDataTable[filtered_columns[0]],
                                                         hovertemplate=dataTableTypeValue + ':<b> %{x}</b><br>' + valueToPlotOnBarGraph +' Return Of '
                                                          + valueToPlotTypeForBarGraph + ': %{y}<extra></extra>')])
                daily_typeDatatableBarChart.update_layout(
                    title = dataTableTypeValue + ' Returns',
                    xaxis_title = dataTableTypeValue,
                    yaxis_title =f'{valueToPlotOnBarGraph} Returns of {dataTableTypeValue}',
                    xaxis=dict(
                        tickmode='linear', 
                        tick0=0,  
                        dtick=1,  
                        automargin=True,  
                        ticks='inside',  
                        tickangle=0 
                    ),
                    hovermode='x unified', hoverdistance=100,
                    yaxis_tickformat='.2f',
                    font=dict(
                        family='Courier New, blue',
                        size=15,
                    color='RebeccaPurple'
                    ),
                    showlegend=False,
                )
                tempDailyPnLDataTable = barGraphDataTable.copy(deep=True)
                column = filtered_columns[0]
                num_winners = len(tempDailyPnLDataTable[tempDailyPnLDataTable[column] > 0])
                num_losers = len(tempDailyPnLDataTable[tempDailyPnLDataTable[column] <= 0])
                total = len(tempDailyPnLDataTable[column])
                dailyPnLDataTable = pd.DataFrame({
                    'Number of Winners': [num_winners],
                    'Number of Losers': [num_losers],
                    'Winners %': [round( (num_winners/total)*100, 2) if total > 0 else 0],
                    'Losers %': [round( (num_losers / total)*100, 2) if total > 0 else 0],
                    'Max Win %': [barGraphDataTable[column].max()],
                    'Max Loss %': [barGraphDataTable[column].min()],
                })
                dailyPnLDataTableDownload = dcc.send_data_frame(dailyPnLDataTable.set_index('Number of Winners').to_csv, 'Youngturtle_All_Days_PnL.csv')
                dailyPnLDataTableReturnPlot = dailyPnLDataTable.to_dict('records')
    
    return [
        filteredChart, yearlyOverlayChart, aggregateChart, superimposedChart,
        allDayDataTableReturnPlot, dayDataTableReturnPlot, 
        specialDayProbabilityChart, specialDayDailyReturnsDataTableReturnPlot, specialDayNthDayReturnsDataTableReturnPlot,
        phenomenaChart, phenomenaDataTableReturnPlot, daily_typeDatatableBarChart, dailyPnLDataTableReturnPlot
    ]

@callback(
    Output(component_id='daily_monthlyVsYearlyReturnsDataTable', component_property='data'),
    [
        Input('daily_symbolNameToPlot', 'value'), Input('daily_chartScaleType', 'value'),
        Input('daily_dataRange', 'start_date'), Input('daily_dataRange', 'end_date'),
        Input('daily_monthlyVsYearlyMonthName', 'value'), Input('daily_monthlyVsYearlyDays', 'value'),
    ]
)
def displayDailyVsMonthly(symbolNameToPlotValue, chartScaleValue,
    startDate, endDate, monthName, monthfirstNDays
):
    df = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/1_Daily.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
    df = df.dropna()
    df['MonthNumber'] = df['Date'].dt.month
    df['WeekNumber'] = df['Date'].dt.strftime('%U').astype(int)
    df['Year'] = df['Date'].dt.year
    df1 = df.copy(deep=True)
    df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)]

    global dailyVsMonthlyDataTableDownload
    dailyVsMonthlyDataTable = pd.DataFrame()
    dailyVsMonthlyDataTableReturnToPlot = dailyVsMonthlyDataTable.to_dict('records')

    monthlyReturnsList = list()
    yearlyReturnsList = list()
    returndf = pd.DataFrame()
        
    if(len(df)>0):
        filtered_df = df.copy(deep=True)
        filtered_df = filtered_df[(filtered_df['MonthNumber']==getMonthNumber(monthName))
                                  & ( (filtered_df['TradingMonthDay']>=1) & (filtered_df['TradingMonthDay']<=monthfirstNDays))
                                ]
        for year in filtered_df['Year'].unique():
            tempdf = filtered_df[filtered_df['Year'] == year]
            first_index = tempdf.head(1).index[0]

            # Check for the start value
            if (first_index > 0):
                if(df1.loc[first_index - 1]['Date'].month == 12):
                    startVal = df1.loc[first_index - 1]['Close']
                else:
                    startVal = np.NaN    
            else:
                startVal = np.NaN

            endVal = tempdf.reset_index(drop=True).iloc[-1]['Close']
           
            if not np.isnan(startVal):
                returnVal = 100 * ((endVal - startVal) / startVal)
                returnVal = round(returnVal, 2)
            else:
                returnVal = np.NaN

            monthlyReturnsList.append(returnVal)
            yearlyReturnsList.append(tempdf.iloc[-1]['YearlyReturnPercentage'])
        
        returndf['Year'] = filtered_df['Year'].unique()
        returndf[f'{monthName}First{monthfirstNDays}DaysROC'] = monthlyReturnsList
        returndf['YearlyReturnPercentage'] = yearlyReturnsList

    if(len(returndf)>0):
        dailyVsMonthlyDataTable = returndf.copy(deep=True)
        allReturnsColumns = dailyVsMonthlyDataTable.columns

        totalCount = [dailyVsMonthlyDataTable[colName][dailyVsMonthlyDataTable[colName] != 0].count() for colName in allReturnsColumns[1:]]
        averageReturns = [round(i, 2) for i in dailyVsMonthlyDataTable[allReturnsColumns[1:]].mean()]
        totalSum = [round(dailyVsMonthlyDataTable[colName][dailyVsMonthlyDataTable[colName] != 0].sum(), 2) for colName in allReturnsColumns[1:]]
        positiveCount = [dailyVsMonthlyDataTable[colName][dailyVsMonthlyDataTable[colName] > 0].count() for colName in allReturnsColumns[1:]]
        positiveMean = [round(dailyVsMonthlyDataTable[colName][dailyVsMonthlyDataTable[colName] > 0].mean(), 2) for colName in allReturnsColumns[1:]]
        positiveSum = [round(dailyVsMonthlyDataTable[colName][dailyVsMonthlyDataTable[colName] > 0].sum(), 2) for colName in allReturnsColumns[1:]]
        negativeCount = [dailyVsMonthlyDataTable[colName][dailyVsMonthlyDataTable[colName] < 0].count() for colName in allReturnsColumns[1:]] 
        negativeMean = [round(dailyVsMonthlyDataTable[colName][dailyVsMonthlyDataTable[colName] < 0].mean(), 2) for colName in allReturnsColumns[1:]]
        negativeSum = [round(dailyVsMonthlyDataTable[colName][dailyVsMonthlyDataTable[colName] < 0].sum(), 2) for colName in allReturnsColumns[1:]]
        
        dailyVsMonthlyDataTable = pd.concat([
            dailyVsMonthlyDataTable,
            pd.DataFrame({value: [[*['All Count'], *totalCount][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        dailyVsMonthlyDataTable = pd.concat([
            dailyVsMonthlyDataTable,
            pd.DataFrame({value: [[*['Positive Count'], *positiveCount][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        dailyVsMonthlyDataTable = pd.concat([
            dailyVsMonthlyDataTable,
            pd.DataFrame({value: [[*['Negative Count'], *negativeCount][i]] for i, value in enumerate(allReturnsColumns)})
        ])

        dailyVsMonthlyDataTable = pd.concat([
            dailyVsMonthlyDataTable,
            pd.DataFrame({value: [[*['Average Return of All'], *averageReturns][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        dailyVsMonthlyDataTable = pd.concat([
            dailyVsMonthlyDataTable,
            pd.DataFrame({value: [[*['Average Return of Positive'], *positiveMean][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        dailyVsMonthlyDataTable = pd.concat([
            dailyVsMonthlyDataTable,
            pd.DataFrame({value: [[*['Average Return of Negative'], *negativeMean][i]] for i, value in enumerate(allReturnsColumns)})
        ])

        dailyVsMonthlyDataTable = pd.concat([
            dailyVsMonthlyDataTable,
            pd.DataFrame({value: [[*['Sum Return of All'], *totalSum][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        dailyVsMonthlyDataTable = pd.concat([
            dailyVsMonthlyDataTable,
            pd.DataFrame({value: [[*['Sum Return of Positive'], *positiveSum][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        dailyVsMonthlyDataTable = pd.concat([
            dailyVsMonthlyDataTable,
            pd.DataFrame({value: [[*['Sum Return of Negative'], *negativeSum][i]] for i, value in enumerate(allReturnsColumns)})
        ])
        dailyVsMonthlyDataTable = dailyVsMonthlyDataTable.fillna(0)
        dailyVsMonthlyDataTableReturnToPlot = dailyVsMonthlyDataTable.to_dict('records')
        dailyVsMonthlyDataTableDownload = dcc.send_data_frame(
            dailyVsMonthlyDataTable.set_index('Year').to_csv, 'Youngturtle_MonthlyFirstNDaysComparisonToYearlyReturns.csv'
            )
        
    return dailyVsMonthlyDataTableReturnToPlot


@callback(
    Output(component_id='daily_allDayDataTable_download_csv', component_property='data'),
    Input('daily_allDayDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def allDayDataTable_download_daily(
    allDayDataTable_download_button
):
    return allDayDataTableDownload

@callback(
    Output(component_id='daily_typeDataTable_download_csv', component_property='data'),
    Input('daily_typeDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def typeDataTable_download_daily(
    typeDataTable_download_button
):
    return dayDataTableDownload

@callback(
    Output(component_id='daily_specialDayDailyReturnsDataTable_download_csv', component_property='data'),
    Input('daily_specialDayDailyReturnsDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def specialDayDailyReturnsDataTable_download_daily(
    specialDayDailyReturnsDataTable_download_button
):
    return specialDayDailyReturnsDataTableDownload

@callback(
    Output(component_id='daily_specialDayNthDayReturnsDataTable_download_csv', component_property='data'),
    Input('daily_specialDayNthDayReturnsDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def specialDayNthDayReturnsDataTable_download_daily(
    specialDayNthDayReturnsDataTable_download_button
):
    return specialDayNthDayReturnsDataTableDownload

@callback(
    Output(component_id='daily_phenomenaDataTable_download_csv', component_property='data'),
    Input('daily_phenomenaDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def phenomenaDataTable_download_daily(
    phenomenaDataTable_download_button
):
    return phenomenaDataTableDownload

@callback(
    Output(component_id='daily_typeDatatablePnL_download_csv', component_property='data'),
    Input('daily_typeDatatablePnL_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def phenomenaDataTable_download_daily(
    DatatablePnL_download_button
):
    return dailyPnLDataTableDownload
        
@callback(
    Output(component_id='daily_monthlyVsYearlyReturnsDataTable_download_csv', component_property='data'),
    Input('daily_monthlyVsYearlyReturnsDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def phenomenaDataTable_download_daily(
    monthlyVsYearlyReturnsDataTable_download_button
):
    return dailyVsMonthlyDataTableDownload
