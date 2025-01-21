from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

from helper import symbolNamesToDropdown, getDataTableForPlot, getDataTableStatistics,\
                    weekDays,getWeeklyScenarioDataFrame,generatePerformanceTable


weeklyAllDayDataTableDownload = pd.DataFrame()
weeklyDataTableDownload = pd.DataFrame()
monthOnMonthDataTableDownload = pd.DataFrame()

weeklyTimeFrameLayout = html.Div([

    html.Br(), html.Br(),
    html.H2('Filtered Weekly Chart Inputs'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Week Type'), width=8, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='weekly_weekType',
                           inline=True,
                           options=[dict(label='Expiry Week', value='3_Expiry'),
                                    dict(label='Mon to Fri', value='2_Monday'),
                                    # dict(label='Mon to Thu', value='2_MonToThu'),
                                    # dict(label='Mon to Wed', value='2_MonToWed'),
                                    # dict(label='Mon to Tue', value='2_MonToTue')
                                    ],
                           value='2_Monday',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=8, align='left'
        )
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Symbol'), width=4, align='left'),
        dbc.Col(html.H6('Select Date Range'), width=4, align='left'),
        dbc.Col(html.H6('Select Chart Scale Type'), width=4, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='weekly_symbolNameToPlot',
                                   options=symbolNamesToDropdown,
                                   value='BANKNIFTY',
                                   clearable=False, maxHeight=300,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.DatePickerRange(id='weekly_dataRange',
                                min_date_allowed=date(1970, 1, 1), max_date_allowed=date(2025, 12, 31),
                                start_date=date(2019, 2, 1), end_date=date(2023, 3, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='weekly_chartScaleType',
                           inline=True,
                           options=[dict(label='Linear', value='linear'),
                                    dict(label='Log', value='log')],
                           value='linear',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        )
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H4('Yearly Filters', style={'color': '#00218fa1'}),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Positive/Negative Years'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd/Leap Years'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='weekly_positiveNegativeYears',
                           inline=True,
                           options=[dict(label='All Years', value='All'),
                                    dict(label='Positive Years only', value=True),
                                    dict(label='Negative Years only', value=False)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='weekly_evenOddYears',
                           inline=True,
                           options=[dict(label='All Years', value='All'),
                                    dict(label='Even Years only', value=True),
                                    dict(label='Odd Years only', value=False), 
                                    dict(label='Leap Years only', value = 2)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H4('Monthly Filters', style={'color': '#00218fa1'}),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Positive/Negative Months'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd Months'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='weekly_positiveNegativeMonths',
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
            dcc.RadioItems(id='weekly_evenOddMonths',
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
    html.Div([dcc.Slider(id='weekly_specificMonthSelection',
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
                         persistence=True, persistence_type='session')],
             style=dict(width='60%')),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H4('Weekly Filters', style={'color': '#00218fa1'}),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Positive/Negative Weeks'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd Weeks(Monthly Count)'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='weekly_positiveNegativeWeeks',
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
            dcc.RadioItems(id='weekly_evenOddWeeksMonthly',
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
        dbc.Col(html.H6('Select Specific Weeks(Monthly Count)'), width=5, align='left'),
        dbc.Col(html.H6('Select Even/Odd Weeks(Yearly Count)'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Slider(id='weekly_specificWeekMonthlySelection',
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
            dcc.RadioItems(id='weekly_evenOddWeeksYearly',
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
    html.H4('Select Percentage Change Range - To Remove Outliers', style={'color': '#00218fa1'}),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('For Weekly'), width=5, align='left'),
        dbc.Col(html.H6('For Monthly'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='weekly_weeklyPercentageChangeSwitch',
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='weekly_monthlyPercentageChangeSwitch',
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        )
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.RangeSlider(id='weekly_weeklyPercentageChange',
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
            html.Div([dcc.RangeSlider(id='weekly_monthlyPercentageChange',
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
            html.Div([daq.BooleanSwitch(id='weekly_yearlyPercentageChangeSwitch',
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        )
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.RangeSlider(id='weekly_yearlyPercentageChange',
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
    html.H2('Filtered Weekly Chart Output'),
    dcc.Graph(id='weekly_filteredChart', style=dict(height='90vh')),


    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Yearly Overlay Weekly Chart'),

    dcc.Graph(id='weekly_yearlyOverlayChart', style=dict(height='90vh')),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Aggregate Weekly Chart Inputs'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Field Name'), width=5, align='left'),
        dbc.Col(html.H6('Select Aggregate Type'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='weekly_aggregateChartFieldName',
                           inline=True,
                           options=[dict(label='Yearly Weeks', value='WeekNumberYearly'),
                                    dict(label='Monthly Weeks', value='WeekNumberMonthly')],
                           value='WeekNumberYearly',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='weekly_aggregateChartType',
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
    html.H2('Aggregate Weekly Chart Output'),
    dcc.Graph(id='weekly_aggregateChart', style=dict(height='90vh')),

    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Superimposed Weekly Chart Inputs'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Superimposed Chart'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='weekly_superimposedChartType',
                           inline=True,
                           options=[dict(label='Yearly Weeks', value='WeekNumberYearly'),
                                    dict(label='Monthly Weeks', value='WeekNumberMonthly')],
                           value='WeekNumberYearly',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.H2('Superimposed Weekly Chart Output'),
    dcc.Graph(id='weekly_superimposedChart', style=dict(height='90vh')),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Data Tables'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select DataTable Type'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='weekly_dataTableType',
                           inline=True,
                           options=[dict(label='Yearly Weeks', value='WeekNumberYearly'),
                                    dict(label='Monthly Weeks', value='WeekNumberMonthly')],
                           value='WeekNumberYearly',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        )
    ]),


    html.Br(), html.Br(),
    dbc.Button(id='weekly_allDayDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='weekly_allDayDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='weekly_allDayDataTable',
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
    dbc.Button(id='weekly_typeDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='weekly_typeDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='weekly_typeDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           page_size=250,
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

    html.Br(), html.Br(),

    # Month on Month Table
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Weekly Scenario Inputs'),

    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select Entry Price Type '), width=4, align='left'),
        dbc.Col(html.H6('Select Exit Price Type '), width=4, align='left'),
        dbc.Col(html.H6('Select Trade Type'), width=4, align='left'),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='daily_monthOnMonthEntryType',
                           inline=True,
                           options=[dict(label='Open', value='Open'),
                                    dict(label='Close', value='Close')],
                           value='Close',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            align='left', width=4,
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_monthOnMonthExitType',
                           inline=True,
                           options=[dict(label='Open', value='Open'),
                                    dict(label='Close', value='Close')],
                           value='Close',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            align='left', width=4,
        ),

        dbc.Col(
            dcc.RadioItems(id='daily_monthOnMonthTradeType',
                           inline=True,
                           options=[dict(label='Long', value='Long'),
                                    dict(label='Short', value='Short')],
                           value='Long',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            align='left', width=4,
        ),
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select Entry Day'), width=4, align='left'),
        dbc.Col(html.H6('Select Exit Day'), width=4, align='left'),
        dbc.Col(html.H6('Select Return type'), width=4, align='left')
    ]),

    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_monthOnMonthEntryDay',
                                   options=weekDays,
                                   value='Monday',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='50%')),
            width=4, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='daily_monthOnMonthExitDay',
                                   options=weekDays,
                                   value='Friday',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='50%')),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='daily_monthOnMonthReturnType',
                           inline=True,
                           options=[dict(label='Percent', value='Percent'),
                                    dict(label='Points', value='Points')],
                           value='Percent',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            align='left', width=4,
        ),
    ]),

    html.Br(),
    html.H2('Weekly Scenario Returns'),
    html.Br(),

    dbc.Button(id='daily_monthOnMonthDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='daily_monthOnMonthDataTable_download_csv'),

    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='daily_monthOnMonthTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'Year',
                                               },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold',
                                               'minWidth': '150px'
                                           },
                                               {
                                               'if': {
                                                   'column_id': 'Total',
                                               },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold',
                                               'minWidth': '70px'
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
            width=10, align='left'
        ),
    ]),

    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),

],
    style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)


@callback(
    [
        Output(component_id='weekly_filteredChart', component_property='figure'),
        Output(component_id='weekly_yearlyOverlayChart', component_property='figure'),
        Output(component_id='weekly_aggregateChart', component_property='figure'),
        Output(component_id='weekly_superimposedChart', component_property='figure'),
        Output(component_id='weekly_allDayDataTable', component_property='data'),
        Output(component_id='weekly_typeDataTable', component_property='data'),
        Output(component_id='daily_monthOnMonthTable', component_property='data'),
    ],
    [
        Input('weekly_weekType', 'value'),
        Input('weekly_symbolNameToPlot', 'value'), Input('weekly_dataRange', 'start_date'), Input('weekly_dataRange', 'end_date'), Input('weekly_chartScaleType', 'value'),
        Input('weekly_positiveNegativeYears', 'value'), Input('weekly_evenOddYears', 'value'),
        Input('weekly_positiveNegativeMonths', 'value'), Input('weekly_evenOddMonths', 'value'), Input('weekly_specificMonthSelection', 'value'),
        Input('weekly_positiveNegativeWeeks', 'value'), Input('weekly_evenOddWeeksMonthly', 'value'),
        Input('weekly_specificWeekMonthlySelection', 'value'), Input('weekly_evenOddWeeksYearly', 'value'),
        Input('weekly_weeklyPercentageChange', 'value'), Input('weekly_weeklyPercentageChangeSwitch', 'on'),
        Input('weekly_monthlyPercentageChange', 'value'), Input('weekly_monthlyPercentageChangeSwitch', 'on'),
        Input('weekly_yearlyPercentageChange', 'value'), Input('weekly_yearlyPercentageChangeSwitch', 'on'),
        Input('weekly_aggregateChartFieldName', 'value'), Input('weekly_aggregateChartType', 'value'),
        Input('weekly_superimposedChartType', 'value'),
        Input('weekly_dataTableType', 'value'),
        Input('daily_monthOnMonthEntryType', 'value'), Input('daily_monthOnMonthExitType', 'value'), 
        Input('daily_monthOnMonthTradeType', 'value'), Input('daily_monthOnMonthEntryDay', 'value'), 
        Input('daily_monthOnMonthExitDay', 'value'), Input('daily_monthOnMonthReturnType', 'value'),
    ]
)
def display_weekly(
    weekTypeValue,
    symbolNameToPlotValue, startDate, endDate, chartScaleValue,
    positiveNegativeYearFilter, evenOddYearFilter,
    positiveNegativeMonthFilter, evenOddMonthFilter, specificMonthSelectionValue,
    positiveNegativeWeekFilter, evenOddWeekMonthlyFilter,
    specificWeekMonthlySelectionValue, evenOddWeekYearlyFilter,
    weeklyPercentageChangeFilter, weeklyPercentageChangeFilterSwitch,
    monthlyPercentageChangeFilter, monthlyPercentageChangeFilterSwitch,
    yearlyPercentageChangeFilter, yearlyPercentageChangeFilterSwitch,
    aggregateChartFieldNameValue, aggregateChartTypeValue,
    superimposedChartTypeValue,
    dataTableTypeValue,
    monthOnMonthEntryType, monthOnMonthExitType, monthOnMonthTradeType,
    monthOnMonthEntryDay, monthOnMonthExitDay, monthOnMonthReturnType
):

    df = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/' + weekTypeValue + 'Weekly.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df = df.dropna()
    initialDates = df.copy(deep=True)['Date']

    # choose date range
    df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)]

    # choose positive/negative, even/odd years
    if (positiveNegativeYearFilter != 'All'):
        df = df[df['PositiveYear'] == positiveNegativeYearFilter]
    if (evenOddYearFilter != 'All'):
        if(evenOddYearFilter != 2):
            df = df[df['EvenYear'] == evenOddYearFilter]
        else:
            df = df[(df['Date'].dt.year % 4 == 0) & ((df['Date'].dt.year % 100 != 0) | (df['Date'].dt.year % 400 == 0))]

    # choose positive/negative, even/odd months
    if (positiveNegativeMonthFilter != 'All'):
        df = df[df['PositiveMonth'] == positiveNegativeMonthFilter]
    if (evenOddMonthFilter != 'All'):
        df = df[df['EvenMonth'] == evenOddMonthFilter]
    if (specificMonthSelectionValue != 0):
        df = df[df['Date'].dt.month == specificMonthSelectionValue]

    # choose positive/negative, even/odd weeks
    if (positiveNegativeWeekFilter != 'All'):
        df = df[df['PositiveWeek'] == positiveNegativeWeekFilter]
    if (evenOddWeekMonthlyFilter != 'All'):
        df = df[df['EvenWeekNumberMonthly'] == evenOddWeekMonthlyFilter]
    if ((specificWeekMonthlySelectionValue != 0) and (specificMonthSelectionValue != 0)):
        df = df[
            (df['WeekNumberMonthly'] == specificWeekMonthlySelectionValue) &
            (df['Date'].dt.month == specificMonthSelectionValue)
        ]
    elif (specificWeekMonthlySelectionValue != 0):
        df = df[df['WeekNumberMonthly'] == specificWeekMonthlySelectionValue]
    if (evenOddWeekYearlyFilter != 'All'):
        df = df[df['EvenWeekNumberYearly'] == evenOddWeekYearlyFilter]

    # add more columns in dataframe
    df['Year'] = df['Date'].dt.year

    # outlier filters
    if (weeklyPercentageChangeFilterSwitch):
        df = df[
            (df['ReturnPercentage'] >= weeklyPercentageChangeFilter[0]) &
            (df['ReturnPercentage'] <= weeklyPercentageChangeFilter[1])
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
    weeklyFilteredChart = go.Figure()
    weeklyYearlyOverlayChart = go.Figure()
    weeklyAggregateChart = go.Figure()
    weeklySuperimposedChart = go.Figure()

    # all return data tables
    weeklyAllDayDataTable = pd.DataFrame()
    weeklyAllDayDataTableReturnPlot = weeklyAllDayDataTable.to_dict('records')
    weeklyDataTable = pd.DataFrame()
    weeklyDataTableReturnPlot = weeklyDataTable.to_dict('records')
    monthOnMonthDataTable = None
    monthOnMonthDF = pd.DataFrame()

    global weeklyAllDayDataTableDownload
    global weeklyDataTableDownload
    global monthOnMonthDataTableDownload

    if (len(df) > 0):

        # create holidays date list only for weekly time frame
        newDates = df.copy(deep=True)['Date']
        notAvailableDates = list(set(initialDates).symmetric_difference(set(newDates)))
        notAvailableWeekEnds = ['sat', 'mon']
        weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        def getNotAvailableDates(x, y): return list((set(x) - set(y))) + list((set(y) - set(x)))

        tradingDates = df['Date'].to_list()
        stratDateOfPlot = tradingDates[0]
        endDateOfPlot = tradingDates[len(tradingDates)-1]
        dateRangeStartToEnd = [
            stratDateOfPlot+timedelta(days=x)for x in range((endDateOfPlot+timedelta(days=1)-stratDateOfPlot).days)
        ]
        notAvailableDates = getNotAvailableDates(dateRangeStartToEnd, tradingDates)

        """
            plot candle sticks filtered chart for weekly only
        """

        returnPercentageList = df['ReturnPercentage'].to_list()
        returnPointsList = df['ReturnPoints'].to_list()
        hoverExtraTextMessageFilteredChart = [
            'change: ' + f'{returnPointsList[i]:.2f}' + ', ' + f'{returnPercentageList[i]:.2f}' + '%'
            for i in range(len(returnPercentageList))
        ]

        weeklyFilteredChart.add_candlestick(
            x=df['Date'],
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            text=hoverExtraTextMessageFilteredChart
        )

        # update chart layout, axis and remove holidays from chart
        weeklyFilteredChart.update_xaxes(
            rangeslider_visible=False,
            rangebreaks=[],
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False, dtick = "M48" if evenOddYearFilter!=False else 'M36',
        )
        weeklyFilteredChart.update_yaxes(
            type=chartScaleValue,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        weeklyFilteredChart.update_layout(
            title='Filtered Weekly Chart',
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
            yearly overlay chart for weekly only
        """

        allYearsListInData = sorted(list(set(df['Year'])))

        for i in range(0, len(allYearsListInData)):
            yearRotationalData = df[df['Year'] == allYearsListInData[i]]
            weeklyYearlyOverlayChart.add_scatter(
                x=yearRotationalData['WeekNumberYearly'],
                y=yearRotationalData['ReturnPercentage'],
                name=allYearsListInData[i]
            )

        weeklyYearlyOverlayChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        weeklyYearlyOverlayChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        weeklyYearlyOverlayChart.update_layout(
            title='Yearly Overlay Weekly Chart',
            xaxis_title='Weeks', xaxis_tickformat='%d-%b(%a)<br>%Y',
            yaxis_title='Percentage Change', yaxis_tickformat='.2f',
            legend_title='Years',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        weeklyYearlyOverlayChart.add_hline(y=0, line_width=1, line_dash='solid', line_color='black')

        """
            aggregate chart for weekly only
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

        weeklyAggregateChart.add_bar(
            x=aggregateDataFrame[aggregateChartFieldNameValue],
            y=aggregateDataFrame['ReturnPercentage'],
            marker=dict(color=np.where(aggregateDataFrame['ReturnPercentage'] < 0, 'red', 'green'))
        )
        weeklyAggregateChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        weeklyAggregateChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        weeklyAggregateChart.update_layout(
            title='Aggregate Weekly Chart',
            xaxis_title='Weeks',
            yaxis_title='Percentage Change', yaxis_tickformat='.2f',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        weeklyAggregateChart.add_hline(y=0, line_width=1, line_dash='solid', line_color='grey')

        """
            super imposed chart for weekly only
        """

        returnsAggregate = pd.DataFrame()
        hoverTextChange = ''

        returnsAggregate = df.groupby(superimposedChartTypeValue)['ReturnPercentage'].mean().reset_index()

        if (superimposedChartTypeValue == 'WeekNumberMonthly'):
            hoverTextChange = '   MTD '
        elif (superimposedChartTypeValue == 'WeekNumberYearly'):
            hoverTextChange = '   YTD '

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
            f'{(xAxisList[i])}' + '<br>' +
            hoverTextChange + 'Return: ' + f'{superImposedReturnList[i]:.2f}' + '%<br>' +
            'Weekly Change: ' + f'{hoverExtraTextMessageSuperimposedChart[i]:.2f}' + '%'
            for i in range(len(hoverExtraTextMessageSuperimposedChart))
        ]

        weeklySuperimposedChart.add_scatter(
            x=returnsAggregate[superimposedChartTypeValue],
            y=returnsAggregate['SuperImposedReturn'],
            text=hoverExtraTextMessageSuperimposedChart,
            hoverinfo='text',
            line=dict(color='black')
        )
        weeklySuperimposedChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        weeklySuperimposedChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        weeklySuperimposedChart.update_layout(
            title='Superimposed Weekly Chart',
            xaxis_title='Weeks',
            yaxis_title='Compounded Percentage Return', yaxis_tickformat='.2f',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        weeklySuperimposedChart.add_hline(y=0, line_width=2, line_dash='solid', line_color='grey')

        """
            dataTable calculation
        """
        allDayReturnPoints = np.array(df['ReturnPercentage'].to_list())

        allDaysStats = getDataTableStatistics(allDayReturnPoints)
        allDayDataTable = pd.concat([weeklyAllDayDataTable, allDaysStats], axis=1)
        allDayDataTable.columns = ['All Weeks']
        weeklyAllDayDataTableReturnValue = getDataTableForPlot(allDayDataTable)
        weeklyAllDayDataTableReturnPlot = weeklyAllDayDataTableReturnValue[0]
        weeklyAllDayDataTableDownload = dcc.send_data_frame(weeklyAllDayDataTableReturnValue[1].to_csv, 'Youngturtle_All_Weeks.csv')

        dataTableColumns = []
        dataTableColumns.extend(range(int(min(df[dataTableTypeValue])), int(max(df[dataTableTypeValue])+1), 1))

        for dayName in dataTableColumns:
            dayReturnPoints = np.array(df[df[dataTableTypeValue] == dayName]['ReturnPercentage'].to_list())
            dayStats = getDataTableStatistics(dayReturnPoints)
            weeklyDataTable = pd.concat([weeklyDataTable, dayStats], axis=1)

        weeklyDataTable.columns = dataTableColumns
        weeklyDataTableReturnValue = getDataTableForPlot(weeklyDataTable)
        weeklyDataTableReturnPlot = weeklyDataTableReturnValue[0]
        weeklyDataTableDownload = dcc.send_data_frame(weeklyDataTableReturnValue[1].to_csv, 'Youngturtle_Individual_Weeks.csv')

        """
        Month on Month Table
        """       
        monthOnMonthInputDf = getWeeklyScenarioDataFrame(weekTypeValue,symbolNameToPlotValue, startDate, endDate, chartScaleValue,
                                                    positiveNegativeYearFilter, evenOddYearFilter,
                                                    positiveNegativeMonthFilter, evenOddMonthFilter, specificMonthSelectionValue,
                                                    positiveNegativeWeekFilter, evenOddWeekMonthlyFilter,
                                                    specificWeekMonthlySelectionValue, evenOddWeekYearlyFilter,
                                                    weeklyPercentageChangeFilter, weeklyPercentageChangeFilterSwitch,
                                                    monthlyPercentageChangeFilter, monthlyPercentageChangeFilterSwitch,
                                                    yearlyPercentageChangeFilter, yearlyPercentageChangeFilterSwitch)
        monthOnMonthDF = generatePerformanceTable(monthOnMonthInputDf, monthOnMonthEntryType, monthOnMonthExitType, monthOnMonthTradeType, monthOnMonthEntryDay, monthOnMonthExitDay, monthOnMonthReturnType)
        
        if monthOnMonthDF is None:
            monthOnMonthDataTable = None
        else:
            monthOnMonthDataTable = monthOnMonthDF.to_dict('records')
            monthOnMonthDataTableDownload = dcc.send_data_frame(monthOnMonthDF.to_csv, 'Youngturtle_MonthOnMonth.csv')

    

    return [weeklyFilteredChart, weeklyYearlyOverlayChart, weeklyAggregateChart, weeklySuperimposedChart,
            weeklyAllDayDataTableReturnPlot, weeklyDataTableReturnPlot, monthOnMonthDataTable]


@callback(
    Output(component_id='weekly_allDayDataTable_download_csv', component_property='data'),
    Input('weekly_allDayDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def allDayDataTable_download_weekly(
    allDayDataTable_download_button
):
    return weeklyAllDayDataTableDownload


@callback(
    Output(component_id='weekly_typeDataTable_download_csv', component_property='data'),
    Input('weekly_typeDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def typeDataTable_download_weekly(
    typeDataTable_download_button
):
    return weeklyDataTableDownload


@callback(
    Output(component_id='daily_monthOnMonthDataTable_download_csv', component_property='data'),
    Input('daily_monthOnMonthDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def monthOnMonthDataTable(
    monthOnMonthDataTable_button
):
    return monthOnMonthDataTableDownload