from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
from itertools import zip_longest
import random


from helper import symbolNamesToDropdown, watchListToDropDown, specialDaysToDropdown, monthFullNames, \
    weekDays, tradingDays, calenderDays, colorDict, \
    getDataTableForPlot, getDataTableStatistics, getMonthNumber, getHistoricTrendingDays, \
    filterDataFrameFromHelper, getTrendingDays, generatePerformanceTable, \
    getRecentDayReturnPercentage, getRecentWeekReturnPercentage, getRecentMonthReturnPercentage

historicTrendDataTableDownload = pd.DataFrame()
trendingStreakDataTableDownload = pd.DataFrame()
watchlistMomentumDatatableDownload = pd.DataFrame()

scenarioLayout = html.Div([
    html.Br(), html.Br(),
    html.H2('Scenario Inputs'),
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
        dbc.Col(html.H6('Select Positive/Negative Years'), width=4, align='left'),
        dbc.Col(html.H6('Select Even/Odd/Leap Years'), width=4, align='left'),
        dbc.Col(html.H6('Select Decade Years'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_positiveNegativeYears',
                           inline=True,
                           options=[dict(label='All Years', value='All'),
                                    dict(label='Positive Years only', value=True),
                                    dict(label='Negative Years only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_evenOddYears',
                           inline=True,
                           options=[dict(label='All Years', value='All'),
                                    dict(label='Even Years only', value=True),
                                    dict(label='Odd Years only', value=False),
                                    dict(label='Leap Years only', value = 2)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_decadeYears',
                                   options=[i for i in range(1, 11)],
                                   value=[i for i in range(1, 11)], multi=True,
                                   clearable=False, maxHeight=250,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
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
                           options=[dict(label='All Weeks', value='All'),
                                    dict(label='Positive Weeks only', value=True),
                                    dict(label='Negative Weeks only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_evenOddExpiryWeeksMonthly',
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
    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),


    # HISTORICALLY TRENDING DAYS
    html.H2('Historically Trending Days'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Trend Type'), width=3, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('Select Consecutive Trending Days'), width=4, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('Select Range of Days'), width=4, align='left', style={'color': '#00218fa1'}),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_historicTrendType',
                           inline=True,
                           options=[dict(label='Bullish', value='Bullish'),
                                    dict(label='Bearish', value='Bearish')],
                           value='Bullish',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='daily_historicTrendConsecutiveDays',
                                 min=2, max=10, step=1,
                                 marks={i: {'label': str(i), 'style': {'color': 'black'}} for i in range(2, 11)},
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='bottom'),
                                 included=False,
                                 value=3,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=4, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='daily_historicTrendDayRange',
                                 min=5, max=25, step=5,
                                 marks={i: {'label': str(i), 'style': {'color': 'black'}} for i in range(5, 26, 5)},
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='bottom'),
                                 included=False,
                                 value=10,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=4, align='left'
        ),
    ]),

    dcc.Graph(id='daily_historicTrendChart', style=dict(height='90vh')),
    html.Br(),

    dbc.Button(id='daily_historicTrendDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_historicTrendDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_historicTrendDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'Date(T)',
                                               },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold',
                                               'minWidth': '150px'
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
            width=12, align='left'
        ),
    ]),


    html.Br(), html.Br(),

    html.Hr(style={'border': '1px solid #00218fa1'}),


    # TRENDING DAY STREAK
    html.H2('Trending Days Streak Input'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Enter Number of Streak Days'), width=4, align='left'),
        dbc.Col(html.H6('Select Week'), width=4, align='left'),
    ]),

    dbc.Row([
        dbc.Col(
            html.Div([dcc.Input(id='daily_trendingStreakValue',
                                type='number', value=5,
                                placeholder='Enter Streak Number',
                                style={'width': '250px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            align='left', width=4,
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='daily_trendingStreakWeekInput',
                                 min=1, max=5, step=1,
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
            dcc.RadioItems(id='daily_trendingStreakType',
                           inline=True,
                           options=[dict(label='Bearish', value='less'),
                                    dict(label='Bullish', value='more')],
                           value='less',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            align='left', width=4,
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='daily_trendingStreakMonthInput',
                                 min=1, max=12, step=1,
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
            html.Div([dcc.Input(id='daily_trendingStreakPercent',
                                type='number', value=0,
                                style={'width': '250px', 'height': '30px'},
                                min=-50, step=0.1,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=4,
            align='left'
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='daily_trendingStreakYearInput',
                                 min=1, max=5, step=1,
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

    html.H2('Trending Days Streak Output'),
    html.Br(),

    dbc.Button(id='daily_trendingDayStreakDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_trendingDayStreakDataTable_download_csv'),

    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_trendingStreakTable',
                                           columns=[
                                               {"name": ["STREAK", "StartDate"], "id": "StartDate"},
                                               {"name": ["STREAK", "StartClose"], "id": "StartClose"},
                                               {"name": ["STREAK", "EndDate"], "id": "EndDate"},
                                               {"name": ["STREAK", "EndClose"], "id": "EndClose"},
                                               {"name": ["STREAK", "TotalDays"], "id": "TotalDays"},
                                               {"name": ["STREAK", "PercentChange"], "id": "PercentChange"},
                                               {"name": ["WEEK", "Date"], "id": "WeekDate"},
                                               {"name": ["WEEK", "Close"], "id": "WeekClose"},
                                               {"name": ["WEEK", "Percent"], "id": "WeekPercent"},
                                               {"name": ["MONTH", "Date"], "id": "MonthDate"},
                                               {"name": ["MONTH", "Close"], "id": "MonthClose"},
                                               {"name": ["MONTH", "Percent"], "id": "MonthPercent"},
                                               {"name": ["YEAR", "Date"], "id": "YearDate"},
                                               {"name": ["YEAR", "Close"], "id": "YearClose"},
                                               {"name": ["YEAR", "Percent"], "id": "YearPercent"},
                                           ],
                                           merge_duplicate_headers=True,
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[
                                               {
                                                   'if': {'column_id': colid},
                                                   'border-right': '1px solid black'
                                               } for colid in ['PercentChange', 'WeekPercent', 'MonthPercent']
                                           ],
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
            width=12, align='left'
        ),
    ]),

    html.Br(), html.Br(),

    # Monthly Momentum Ranking
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Momentum Ranking'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Watchlist'), width=4, align='left'),
        dbc.Col(html.H6('Select Trend'), width=4, align='left'),
        dbc.Col(html.H6('Enter ATR Period'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_momentumRankingWatchlist',
                                   options=watchListToDropDown,
                                   value=watchListToDropDown[0],
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_momentumRankingTrendType',
                           inline=True,
                           options=[dict(label='Bullish', value=0),
                                    dict(label='Bearish', value=1),
                                    dict(label='Any', value=-1)],
                           value=-1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='daily_momentumRankingATRPeriod',
                                type='number', placeholder='Select ATR Period',
                                required=True,
                                style={'width': '250px', 'height': '30px'},
                                min=1, max=1000, step=1, value=1,
                                persistence=True,
                                persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=4, align='left'
        ),
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='daily_momentumRankingRecentDays1ATRSwitch',  # type: ignore
                                        on=True, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='daily_momentumRankingRecentDays2ATRSwitch',  # type: ignore
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        )
    ]),
    dbc.Row([
        dbc.Col(html.H6('Enter Recent Days 1'), width=5, align='left'),
        dbc.Col(html.H6('Enter Recent Days 2'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Input(id='daily_momentumRankingRecentDays1',
                                type='number', placeholder='Enter Number',
                                style={'width': '250px', 'height': '30px'},
                                min=0, step=1, value=10,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='daily_momentumRankingRecentDays2',
                                type='number', placeholder='Enter Number',
                                style={'width': '250px', 'height': '30px'},
                                min=0, step=1, value=20,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='daily_momentumRankingRecentMonths1ATRSwitch',  # type: ignore
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='daily_momentumRankingRecentMonths2ATRSwitch',  # type: ignore
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        ),
    ]),
    dbc.Row([
        dbc.Col(html.H6('Enter Recent Months 1'), width=5, align='left'),
        dbc.Col(html.H6('Enter Recent Months 2'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Input(id='daily_momentumRankingRecentMonths1',
                                type='number', placeholder='Enter Number',
                                style={'width': '250px', 'height': '30px'},
                                min=0, step=1, value=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='daily_momentumRankingRecentMonths2',
                                type='number', placeholder='Enter Number',
                                style={'width': '250px', 'height': '30px'},
                                min=0, step=1, value=3,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    dbc.Button(id='daily_momentumRankingDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_momentumRankingDataTable_download_csv'),

    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_momentumRankingDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'Index',
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

    # Watchlist Analysis
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Watchlist Analysis'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Watchlist'), width=5, align='left'),

    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_watchlistPercentageReturnToPlot',
                                   options=watchListToDropDown,
                                   value=watchListToDropDown[0],
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=5, align='left'
        )
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Recent Week'), width=5, align='left'),
        dbc.Col(html.H6('Select Recent Month 1'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Input(id='daily_watchlistPercentageReturnRecentWeek',
                                type='number', placeholder='Select Recent Day 2',
                                style={'width': '250px', 'height': '30px'},
                                min=1, max=4, step=1, value=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='daily_watchlistPercentageReturnRecentMonth1',
                                type='number', placeholder='Select Recent Month 1',
                                required=True,
                                style={'width': '250px', 'height': '30px'},
                                min=1, max=12, step=1, value=1,
                                persistence=True,
                                persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=4, align='left'
        ),
    ]),
    dbc.Row([
        dbc.Col(html.H6('Select Recent Month 2'), width=5, align='left'),
        dbc.Col(html.H6('Select Recent Month 3'), width=5, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Input(id='daily_watchlistPercentageReturnRecentMonth2',
                                type='number', placeholder='Select Recent Month 2',
                                required=True,
                                style={'width': '250px', 'height': '30px'},
                                min=1, max=24, step=1, value=3,
                                persistence=True,
                                persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='daily_watchlistPercentageReturnRecentMonth3',
                                type='number', placeholder='Select Recent Month 3',
                                required=True,
                                style={'width': '250px', 'height': '30px'},
                                min=1, max=36, step=1, value=12,
                                persistence=True,
                                persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
            width=5, align='left'
        )
    ]),

    html.Br(),
    dcc.Graph(id='daily_watchlistPercentageReturn', style={'overflow-x': 'scroll', 'height': '90vh'}),
    # END-----------------

    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
],
    style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)

@callback(
    [
        Output(component_id='daily_historicTrendChart', component_property='figure'),
        Output(component_id='daily_historicTrendDataTable', component_property='data'),
        Output(component_id='daily_trendingStreakTable', component_property='data'),
        Output(component_id='daily_momentumRankingDataTable', component_property='data'),
        Output(component_id='daily_watchlistPercentageReturn', component_property='figure'),
    ],
    [
        Input('daily_symbolNameToPlot', 'value'), Input('daily_chartScaleType', 'value'),
        Input('daily_dataRange', 'start_date'), Input('daily_dataRange', 'end_date'), Input('daily_dateLastNDays', 'value'),
        Input('daily_positiveNegativeYears', 'value'), Input('daily_evenOddYears', 'value'), Input('daily_decadeYears', 'value'),
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
        Input('daily_historicTrendType', 'value'), Input('daily_historicTrendConsecutiveDays', 'value'), Input('daily_historicTrendDayRange', 'value'),
        Input('daily_trendingStreakValue', 'value'), Input('daily_trendingStreakType', 'value'), Input('daily_trendingStreakPercent', 'value'),
        Input('daily_trendingStreakWeekInput', 'value'), Input('daily_trendingStreakMonthInput', 'value'), Input('daily_trendingStreakYearInput', 'value'),
        Input('daily_momentumRankingWatchlist', 'value'), Input('daily_momentumRankingTrendType', 'value'),
        Input('daily_momentumRankingATRPeriod', 'value'),
        Input('daily_momentumRankingRecentDays1', 'value'), Input('daily_momentumRankingRecentDays2', 'value'),
        Input('daily_momentumRankingRecentMonths1', 'value'), Input('daily_momentumRankingRecentMonths2', 'value'),
        Input('daily_momentumRankingRecentDays1ATRSwitch', 'on'), Input('daily_momentumRankingRecentDays2ATRSwitch', 'on'),
        Input('daily_momentumRankingRecentMonths1ATRSwitch', 'on'), Input('daily_momentumRankingRecentMonths2ATRSwitch', 'on'),
        Input('daily_watchlistPercentageReturnToPlot', 'value'),
        Input('daily_watchlistPercentageReturnRecentWeek', 'value'), Input('daily_watchlistPercentageReturnRecentMonth1', 'value'),
        Input('daily_watchlistPercentageReturnRecentMonth2', 'value'), Input('daily_watchlistPercentageReturnRecentMonth3', 'value'),
    ]
)

def displayScenario(symbolNameToPlotValue, chartScaleValue,
    startDate, endDate, dateLastNDaysValue,
    positiveNegativeYearFilter, evenOddYearFilter, decadeYearsValue,
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
    historicTrendType, historicTrendConsecutiveDays, historicTrendDayRange,
    trendingStreakValue, trendingStreakType, trendingStreakPercent,
    trendingStreakWeekInput, trendingStreakMonthInput, trendingStreakYearInput,
    watchlistMomentumToPlotValue, watchlistMomentumTrendType,  watchlistMomentumATRPeriodValue,
    recentDayMomentumValue1, recentDayMomentumValue2,
    recentMonthMomentumValue1, recentMonthMomentumValue2,
    recentDayMomentumValue1ATRSwitch, recentDayMomentumValue2ATRSwitch,
    recentMonthMomentumValue1ATRSwitch, recentMonthMomentumValue2ATRSwitch,
    watchlistPercentageReturnToPlotValue,
    watchlistPercentageRecentWeekValue, watchListPercentageReturnMonthValue1,
    watchListPercentageReturnMonthValue2, watchListPercentageReturnMonthValue3,
):
    df = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/1_Daily.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
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
        if(evenOddYearFilter != 2):
            df = df[df['EvenYear'] == evenOddYearFilter]
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
    
    #All Return figures 
    historicTrendChart = go.Figure()
    watchlistReturnfigure = go.Figure()
    
    # All Return Datatables
    historicTrendDataTable = pd.DataFrame()
    historicTrendDataTableReturnPlot = historicTrendDataTable.to_dict('records')
    trendingStreakDataTable = pd.DataFrame()
    watchlistMomentumDatatable = pd.DataFrame()
    watchlistMomentumDatatableReturnPlot = watchlistMomentumDatatable.to_dict('records')

    # All Datatables to download
    global historicTrendDataTableDownload
    global trendingStreakDataTableDownload
    global watchlistMomentumDatatableDownload

    if(len(df)>0):
        """
            Historical Trending Days Calculations
        """
        historicTrendDayData = df.copy(deep=True)
        historicTrendColumns = ['Date(T)', *['T'+str(i) for i in range(-historicTrendDayRange, 0)], *['T+'+str(i) for i in range(1, historicTrendDayRange+1)]]
        totalReturns = []

        historicTrendDayData['ConsecutiveDays'] = getHistoricTrendingDays(
            historicTrendDayData['ReturnPoints'].to_list(),
            historicTrendType, historicTrendConsecutiveDays, historicTrendDayRange
        )
        historicTrendDayData = historicTrendDayData[
            (historicTrendDayData['ConsecutiveDays'] == 0) | (historicTrendDayData['ConsecutiveDays'] == 1)
        ]
        firstStreakDates = historicTrendDayData[historicTrendDayData['ConsecutiveDays'] == 1]['Date'].to_list()

        for firstStreakDate in firstStreakDates:
            beforeDaysReturn = historicTrendDayData[historicTrendDayData['Date'] <= firstStreakDate][-historicTrendDayRange:]['ReturnPercentage'].to_list()
            afterDaysReturn = historicTrendDayData[historicTrendDayData['Date'] > firstStreakDate][:historicTrendDayRange]['ReturnPercentage'].to_list()
            totalReturns = [*totalReturns, [firstStreakDate, *beforeDaysReturn, *afterDaysReturn]]

        historicTrendDataTable = pd.DataFrame(totalReturns, columns=historicTrendColumns)

        totalCount = [historicTrendDataTable[colName].count() for colName in historicTrendColumns[1:]]
        averageReturns = [round(i, 2) for i in historicTrendDataTable[historicTrendColumns[1:]].mean()]
        totalSum = [round(historicTrendDataTable[colName][historicTrendDataTable[colName] != 0].sum(), 2) for colName in historicTrendColumns[1:]]

        positiveCount = [historicTrendDataTable[colName][historicTrendDataTable[colName] > 0].count() for colName in historicTrendColumns[1:]]
        positiveMean = [round(historicTrendDataTable[colName][historicTrendDataTable[colName] > 0].mean(), 2) for colName in historicTrendColumns[1:]]
        positiveSum = [round(historicTrendDataTable[colName][historicTrendDataTable[colName] > 0].sum(), 2) for colName in historicTrendColumns[1:]]

        negativeCount = [historicTrendDataTable[colName][historicTrendDataTable[colName] < 0].count() for colName in historicTrendColumns[1:]]
        negativeMean = [round(historicTrendDataTable[colName][historicTrendDataTable[colName] < 0].mean(), 2) for colName in historicTrendColumns[1:]]
        negativeSum = [round(historicTrendDataTable[colName][historicTrendDataTable[colName] < 0].sum(), 2) for colName in historicTrendColumns[1:]]

        superimposedReturns = [(i/100)+1 for i in averageReturns]

        for i in range(0, historicTrendDayRange):
            if (i == 0):
                superimposedReturns[historicTrendDayRange-i-1] = superimposedReturns[historicTrendDayRange-i-1]
                superimposedReturns[historicTrendDayRange+i] = superimposedReturns[historicTrendDayRange]
            else:
                superimposedReturns[historicTrendDayRange-i-1] = (
                    superimposedReturns[historicTrendDayRange-i]*superimposedReturns[historicTrendDayRange-i-1]
                )
                superimposedReturns[historicTrendDayRange+i] = (
                    superimposedReturns[historicTrendDayRange+i-1]*superimposedReturns[historicTrendDayRange+i]
                )

        try:
            superimposedReturns = [round((i-1)*100, 2) for i in superimposedReturns]
            historicTrendDataTable['Date(T)'] = historicTrendDataTable['Date(T)'].dt.strftime('%d-%m-%Y')
        except AttributeError:
            print('Error in date type cast of date in Historical Trend Day')

        historicTrendDataTable = pd.concat([
            historicTrendDataTable,
            pd.DataFrame({value: [[*['All Count'], *totalCount][i]] for i, value in enumerate(historicTrendColumns)})
        ])
        historicTrendDataTable = pd.concat([
            historicTrendDataTable,
            pd.DataFrame({value: [[*['Positive Count'], *positiveCount][i]] for i, value in enumerate(historicTrendColumns)})
        ])
        historicTrendDataTable = pd.concat([
            historicTrendDataTable,
            pd.DataFrame({value: [[*['Negative Count'], *negativeCount][i]] for i, value in enumerate(historicTrendColumns)})
        ])

        historicTrendDataTable = pd.concat([
            historicTrendDataTable,
            pd.DataFrame({value: [[*['Average Return of All'], *averageReturns][i]] for i, value in enumerate(historicTrendColumns)})
        ])
        historicTrendDataTable = pd.concat([
            historicTrendDataTable,
            pd.DataFrame({value: [[*['Average Return of Positive'], *positiveMean][i]] for i, value in enumerate(historicTrendColumns)})
        ])
        historicTrendDataTable = pd.concat([
            historicTrendDataTable,
            pd.DataFrame({value: [[*['Average Return of Negative'], *negativeMean][i]] for i, value in enumerate(historicTrendColumns)})
        ])

        historicTrendDataTable = pd.concat([
            historicTrendDataTable,
            pd.DataFrame({value: [[*['Sum Return of All'], *totalSum][i]] for i, value in enumerate(historicTrendColumns)})
        ])
        historicTrendDataTable = pd.concat([
            historicTrendDataTable,
            pd.DataFrame({value: [[*['Sum Return of Positive'], *positiveSum][i]] for i, value in enumerate(historicTrendColumns)})
        ])
        historicTrendDataTable = pd.concat([
            historicTrendDataTable,
            pd.DataFrame({value: [[*['Sum Return of Negative'], *negativeSum][i]] for i, value in enumerate(historicTrendColumns)})
        ])

        historicTrendDataTable = pd.concat([
            historicTrendDataTable,
            pd.DataFrame({value: [[*['Superimposed Returns'], *superimposedReturns][i]] for i, value in enumerate(historicTrendColumns)})
        ])

        historicTrendDataTable = historicTrendDataTable.fillna(0)

        historicTrendChart.add_scatter(
            x=historicTrendColumns[1:],
            y=superimposedReturns,
            line=dict(color='black')
        )
        historicTrendChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        historicTrendChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        historicTrendChart.update_layout(
            title='Superimposed Returns Before-After Trending Days Daily Chart',
            xaxis_title='Days',
            yaxis_title='Compounded Percentage Return', yaxis_tickformat='.2f',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        historicTrendChart.add_hline(y=0, line_width=1, line_dash='solid', line_color='black')
        historicTrendChart.add_vline(x='T-1', line_width=1, line_dash='solid', line_color='black')
        historicTrendChart.add_vline(x='T+1', line_width=1, line_dash='solid', line_color='black')

        historicTrendDataTableReturnPlot = historicTrendDataTable.to_dict('records')

        historicTrendDataTableDownload = dcc.send_data_frame(historicTrendDataTable.set_index('Date(T)').to_csv, 'Youngturtle_historicalTrendingDays.csv')

        """
            Trending Streak Days
        """
        trendingStreakDF = getTrendingDays(df, trendingStreakValue, trendingStreakType, trendingStreakPercent, trendingStreakWeekInput, trendingStreakMonthInput, trendingStreakYearInput)
        if trendingStreakDF is None:
            trendingStreakDataTable = None
        else:
            trendingStreakDataTable = trendingStreakDF.to_dict('records')
            trendingStreakDataTableDownload = dcc.send_data_frame(trendingStreakDF.to_csv, 'Youngturtle_TrendingDayStreak.csv')

        """
            Momentum Ranking
        """
        ATR_AvgValue = 0
        col6, col7, col8, col9 = None, None, None, None
        if (recentDayMomentumValue1 is not None
            and recentDayMomentumValue2 is not None
            and recentMonthMomentumValue1 is not None
            and recentMonthMomentumValue2 is not None
            and watchlistMomentumATRPeriodValue is not None
            ):
            col1 = f'{recentDayMomentumValue1} Days' if recentDayMomentumValue1 > 1 else f'{recentDayMomentumValue1} Day'
            col2 = f'{recentDayMomentumValue2} Days' if recentDayMomentumValue2 > 1 else f'{recentDayMomentumValue2} Day'
            col3 = f'{recentMonthMomentumValue1} Month' if recentMonthMomentumValue1 < 2 else f'{recentMonthMomentumValue1} Months'
            col4 = f'{recentMonthMomentumValue2} Month' if recentMonthMomentumValue2 < 2 else f'{recentMonthMomentumValue2} Months'
            col5 = f'ATR Percentage ({watchlistMomentumATRPeriodValue})'

            if (recentDayMomentumValue1ATRSwitch):
                col6 = f'Dual Average Recent Day({recentDayMomentumValue1})'
            if (recentDayMomentumValue2ATRSwitch):
                col7 = f'Dual Average Recent Day({recentDayMomentumValue2})'
            if (recentMonthMomentumValue1ATRSwitch):
                col8 = f'Dual Average Recent Month({recentMonthMomentumValue1})'
            if (recentMonthMomentumValue2ATRSwitch):
                col9 = f'Dual Average Recent Month({recentMonthMomentumValue2})'

            if (recentDayMomentumValue1 == recentDayMomentumValue2):
                col2 = f'{recentDayMomentumValue2} Days_' if recentDayMomentumValue2 > 1 else f'{recentDayMomentumValue2} Day_'
            if (recentMonthMomentumValue1 == recentMonthMomentumValue2):
                col4 = f'{recentMonthMomentumValue2} Month_' if recentMonthMomentumValue2 < 2 else f'{recentMonthMomentumValue2} Months_'

            rankingList1, rankingList2, rankingList3, rankingList4, rankingList5 = list(), list(), list(), list(), list()
            tempDict = dict()
            symbolsToPlot = pd.read_csv('./Watchlist' + '//' + 'Watchlist.csv')[watchlistMomentumToPlotValue].unique()

            for symbol in symbolsToPlot:
                if symbol in symbolNamesToDropdown:
                    df = pd.read_csv('./Symbols//' + symbol + '//' + '1_Daily.csv')
                    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
                    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
                    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
                    df = df.dropna(how='all')
                    df = df.fillna(0)
                    df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)].reset_index(drop=True)
                    df['ATR_Percentage'] = [
                        round((max(abs(df.loc[i]['High'] - df.loc[i]['Low']),
                                    abs(df.loc[i]['High'] - df.loc[i-1]['Close']),
                                    abs(df.loc[i]['Low'] - df.loc[i-1]['Close']))/df.loc[i-1]['Close'])*100, 2) if (i >= 1)
                        else np.nan
                        for i in range(0, len(df))
                    ]
                    if (watchlistMomentumATRPeriodValue == 1):
                        df[col5] = df['ATR_Percentage']

                    else:
                        df[col5] = [
                            round(df.loc[i+1-watchlistMomentumATRPeriodValue:i]['ATR_Percentage'].mean(), 2)
                            if (i >= watchlistMomentumATRPeriodValue)
                            else np.nan
                            for i in range(0, len(df))
                        ]

                    if (len(df) > 0):
                        lastNDayMomentum1 = getRecentDayReturnPercentage(df, recentDayMomentumValue1)
                        lastNDayMomentum2 = getRecentDayReturnPercentage(df, recentDayMomentumValue2)
                        lastMonthMomentum1 = getRecentMonthReturnPercentage(df, recentMonthMomentumValue1)
                        lastMonthMomentum2 = getRecentMonthReturnPercentage(df, recentMonthMomentumValue2)
                        bullishCheck = (lastNDayMomentum1 > 0) and (lastNDayMomentum2 > 0) and (lastMonthMomentum1 > 0) and (lastMonthMomentum2 > 0)
                        ATR_AvgValue = df.loc[len(df)-1][col5]

                        if ((watchlistMomentumTrendType == 0) and bullishCheck):
                            tempDict[symbol] = [lastNDayMomentum1, lastNDayMomentum2, lastMonthMomentum1, lastMonthMomentum2, ATR_AvgValue]
                        elif ((watchlistMomentumTrendType == 1) and (not bullishCheck)):
                            tempDict[symbol] = [lastNDayMomentum1, lastNDayMomentum2, lastMonthMomentum1, lastMonthMomentum2, ATR_AvgValue]
                        elif (watchlistMomentumTrendType == -1):
                            tempDict[symbol] = [lastNDayMomentum1, lastNDayMomentum2, lastMonthMomentum1, lastMonthMomentum2, ATR_AvgValue]

            if (len(tempDict) > 0):
                tempdf = pd.DataFrame.from_dict(tempDict, orient='index', columns=[col1, col2, col3, col4, col5])
                tempdf.reset_index(inplace=True)
                tempdf.rename(columns={'index': 'Symbol'}, inplace=True)
                sortedList1 = tempdf.sort_values(by=col1, ascending=False)[col1].to_list()
                sortedList2 = tempdf.sort_values(by=col2, ascending=False)[col2].to_list()
                sortedList3 = tempdf.sort_values(by=col3, ascending=False)[col3].to_list()
                sortedList4 = tempdf.sort_values(by=col4, ascending=False)[col4].to_list()
                sortedList5 = tempdf.sort_values(by=col5, ascending=False)[col5].to_list()
                symbolList = tempdf['Symbol'].to_list()

                for symbol in symbolList:
                    index1 = sortedList1.index(tempdf.loc[tempdf['Symbol'] == symbol][col1].values[0]) + 1
                    index2 = sortedList2.index(tempdf.loc[tempdf['Symbol'] == symbol][col2].values[0]) + 1
                    index3 = sortedList3.index(tempdf.loc[tempdf['Symbol'] == symbol][col3].values[0]) + 1
                    index4 = sortedList4.index(tempdf.loc[tempdf['Symbol'] == symbol][col4].values[0]) + 1
                    index5 = sortedList5.index(tempdf.loc[tempdf['Symbol'] == symbol][col5].values[0]) + 1
                    rankingList1.append(index1)
                    rankingList2.append(index2)
                    rankingList3.append(index3)
                    rankingList4.append(index4)
                    rankingList5.append(index5)

                watchlistMomentumDatatable = pd.DataFrame({
                    'Index': [i+1 for i in range(0, len(symbolList))],
                    'Symbol': symbolList,
                    col1: rankingList1,
                    col2: rankingList2,
                    col3: rankingList3,
                    col4: rankingList4,
                    'Average of Rankings': [round((a+b+c+d) / 4, 2) for a, b, c, d in zip(rankingList1, rankingList2, rankingList3, rankingList4)],
                    col5: tempdf[col5].to_list(),
                    col5.replace(f'({watchlistMomentumATRPeriodValue})', '')+' Ranking': rankingList5,
                })

                if (col9 != None):
                    watchlistMomentumDatatable[col9] = [round((a+b) / 2, 2) for a, b in zip(rankingList4, rankingList5)]
                elif (col8 != None):
                    watchlistMomentumDatatable[col8] = [round((a+b) / 2, 2) for a, b in zip(rankingList3, rankingList5)]
                elif (col7 != None):
                    watchlistMomentumDatatable[col7] = [round((a+b) / 2, 2) for a, b in zip(rankingList2, rankingList5)]
                elif (col6 != None):
                    watchlistMomentumDatatable[col6] = [round((a+b) / 2, 2) for a, b in zip(rankingList1, rankingList5)]

                watchlistMomentumDatatableDownload = dcc.send_data_frame(
                    watchlistMomentumDatatable.to_csv, 'Youngturtle_momentumBasedRanking.csv', index=False
                )

                watchlistMomentumDatatableReturnPlot = watchlistMomentumDatatable.to_dict('records')

        """
            Watchlist Analysis
        """
        if (
            watchlistPercentageRecentWeekValue is not None and watchListPercentageReturnMonthValue1 is not None
            and watchListPercentageReturnMonthValue2 is not None and watchListPercentageReturnMonthValue3 is not None
        ):
            col1 = f'{watchlistPercentageRecentWeekValue} Week' if watchlistPercentageRecentWeekValue < 2 else f'{watchlistPercentageRecentWeekValue} Weeks'
            col2 = f'{watchListPercentageReturnMonthValue1} Month' if watchListPercentageReturnMonthValue1 < 2 else f'{watchListPercentageReturnMonthValue1} Months'
            col3 = f'{watchListPercentageReturnMonthValue2} Month' if watchListPercentageReturnMonthValue2 < 2 else f'{watchListPercentageReturnMonthValue2} Months'
            col4 = f'{watchListPercentageReturnMonthValue3} Month' if watchListPercentageReturnMonthValue3 < 2 else f'{watchListPercentageReturnMonthValue3} Months'

            if (watchListPercentageReturnMonthValue1 == watchListPercentageReturnMonthValue2):
                col3 = f'{watchListPercentageReturnMonthValue2} Month_' if watchListPercentageReturnMonthValue2 < 2 else f'{watchListPercentageReturnMonthValue2} Months__'
            if (watchListPercentageReturnMonthValue1 == watchListPercentageReturnMonthValue3 or watchListPercentageReturnMonthValue2 == watchListPercentageReturnMonthValue3):
                col4 = f'{watchListPercentageReturnMonthValue3} Month__' if watchListPercentageReturnMonthValue3 < 2 else f'{watchListPercentageReturnMonthValue3} Months__'

            tempDict = dict()
            symbolsToPlot = pd.read_csv('./Watchlist' + '//' + 'Watchlist.csv')[watchlistPercentageReturnToPlotValue].unique()
            watchlistSymbolCount = 0

            for symbol in symbolsToPlot:
                if symbol in symbolNamesToDropdown:
                    watchlistSymbolCount = watchlistSymbolCount + 1
                    df = pd.read_csv('./Symbols//' + symbol + '//' + '1_Daily.csv')
                    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
                    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
                    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
                    df = df.dropna(how='all')
                    df = df.fillna(0)
                    df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)].reset_index(drop=True)
                    if (len(df) > 0):
                        weekReturnValue = getRecentWeekReturnPercentage(df, watchlistPercentageRecentWeekValue)
                        monthReturnValue1 = getRecentMonthReturnPercentage(df, watchListPercentageReturnMonthValue1)
                        monthReturnValue2 = getRecentMonthReturnPercentage(df, watchListPercentageReturnMonthValue2)
                        monthReturnValue3 = getRecentMonthReturnPercentage(df, watchListPercentageReturnMonthValue3)
                        tempDict[symbol] = [weekReturnValue, monthReturnValue1, monthReturnValue2, monthReturnValue3]

            tempdf = pd.DataFrame.from_dict(tempDict, orient='index', columns=[col1, col2, col3, col4])
            tempdf.reset_index(inplace=True)
            tempdf.rename(columns={'index': 'Symbol'}, inplace=True)

            for col in [col1, col2, col3, col4]:
                watchlistReturnfigure.add_trace(
                    go.Bar(
                        x=tempdf['Symbol'], y=tempdf[col], name=col, orientation='v',
                    )
                )

            watchlistReturnfigure.update_xaxes(
                rangeslider_visible=False,
                showline=True, linewidth=1, linecolor='grey',
                gridcolor='grey', griddash='dot',
                showspikes=True, spikemode='across', spikesnap='cursor',
                spikecolor='grey', spikethickness=1, spikedash='dash',
                fixedrange=False
            )
            watchlistReturnfigure.update_yaxes(
                showline=True, linewidth=1, linecolor='grey',
                gridcolor='grey', griddash='dot',
                showspikes=True, spikemode='across', spikesnap='cursor',
                spikecolor='grey', spikethickness=1, spikedash='dash',
                fixedrange=False
            )
            watchlistReturnfigure.update_layout(
                title='Watchlist Return Percentage Chart',
                xaxis_title='Symbol',
                yaxis_title='Percentage Return', yaxis_tickformat='.2f',
                autosize=False, width=max(400, watchlistSymbolCount*180),
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
            watchlistReturnfigure.add_hline(y=0, line_width=1, line_dash='solid', line_color='grey')
    
    else:
        print("Based on available filters, the resulting filtered data is empty")
    
    """
        End of first level code
    """
    return [historicTrendChart, historicTrendDataTableReturnPlot,
        trendingStreakDataTable,
        watchlistMomentumDatatableReturnPlot,
        watchlistReturnfigure]    

@callback(
    Output(component_id='daily_historicTrendDataTable_download_csv', component_property='data'),
    Input('daily_historicTrendDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def historicTrend_download_daily(
    historicTrendDataTable_download_button
):
    return historicTrendDataTableDownload


@callback(
    Output(component_id='daily_trendingDayStreakDataTable_download_csv', component_property='data'),
    Input('daily_trendingDayStreakDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def trendingDayStreakDataTable(
    trendingDayStreakDataTable_button
):
    return trendingStreakDataTableDownload


@callback(
    Output(component_id='daily_momentumRankingDataTable_download_csv', component_property='data'),
    Input('daily_momentumRankingDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def monentumDataTable_download_daily(
    momentumDataTable_download_button
):
    return watchlistMomentumDatatableDownload


