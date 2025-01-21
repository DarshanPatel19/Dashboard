from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

from helper import symbolNamesToDropdown, monthNames, monthFullNames, getDataTableForPlot, getDataTableStatistics, getMonthNumber


monthlyAllDayDataTableDownload = pd.DataFrame()
monthlyDataTableDownload = pd.DataFrame()
monthlyYearOnYearReturnsDataTableDownload = pd.DataFrame()
historicallyTrendingMonthsDataTableDownload = pd.DataFrame()


monthlyTimeFrameLayout = html.Div([

    html.Br(), html.Br(),
    html.H2('Filtered Monthly Chart Inputs'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Month Type'), width=8, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='monthly_monthType',
                           inline=True,
                           options=[dict(label='Expiry Month', value='5_MonthlyExpiry'),
                                    dict(label='Calender Month', value='4_Monthly')],
                           value='4_Monthly',
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
            html.Div([dcc.Dropdown(id='monthly_symbolNameToPlot',
                                   options=symbolNamesToDropdown,
                                   value='BANKNIFTY',
                                   clearable=False, maxHeight=300,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.DatePickerRange(id='monthly_dataRange',
                                min_date_allowed=date(1970, 1, 1), max_date_allowed=date(2025, 12, 31),
                                start_date=date(2016, 1, 1), end_date=date(2023, 12, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='monthly_chartScaleType',
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
            dcc.RadioItems(id='monthly_positiveNegativeYears',
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
            dcc.RadioItems(id='monthly_evenOddYears',
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
            dcc.RadioItems(id='monthly_positiveNegativeMonths',
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
            dcc.RadioItems(id='monthly_evenOddMonths',
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
    html.Div([dcc.Slider(id='monthly_specificMonthSelection',
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
    html.H4('Select Percentage Change Range - To Remove Outliers', style={'color': '#00218fa1'}),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('For Monthly'), width=5, align='left'),
        dbc.Col(html.H6('For Yearly'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='monthly_monthlyPercentageChangeSwitch',
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='monthly_yearlyPercentageChangeSwitch',
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        )
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.RangeSlider(id='monthly_monthlyPercentageChange',
                                      min=-25, max=25,
                                      marks={str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(-25, 26, 5)},
                                      dots=False, updatemode='drag', allowCross=False,
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      value=[-10, 10],
                                      persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.RangeSlider(id='monthly_yearlyPercentageChange',
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
    html.H2('Filtered Monthly Chart Output'),
    dcc.Graph(id='monthly_filteredChart', style=dict(height='90vh')),


    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Yearly Overlay Monthly Chart'),

    dcc.Graph(id='monthly_yearlyOverlayChart', style=dict(height='90vh')),


    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Aggregate Monthly Chart Inputs'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Aggregate Type'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='monthly_aggregateChartType',
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
    html.H2('Aggregate Monthly Chart Output'),
    dcc.Graph(id='monthly_aggregateChart', style=dict(height='90vh')),


    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Superimposed Monthly Chart'),

    dcc.Graph(id='monthly_superimposedChart', style=dict(height='90vh')),


    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Data Tables'),

    html.Br(), html.Br(),
    dbc.Button(id='monthly_allDayDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='monthly_allDayDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='monthly_allDayDataTable',
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
    dbc.Button(id='monthly_typeDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='monthly_typeDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='monthly_typeDataTable',
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
    dbc.Button(id='monthly_yearOnYearReturnsDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='monthly_yearOnYearReturnsDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='monthly_yearOnYearReturnsDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           page_size=250,
                                           style_data_conditional=[
                                               {
                                                   'if': {
                                                       'column_id': 'Year',
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
                                               }
                                           ] +
                                           [
                                               {
                                                   'if': {
                                                       'filter_query': '{'+col+'} >= 0',
                                                       'column_id': ''+col+''
                                                   },
                                                   'backgroundColor': 'lightgreen'
                                               } for col in monthNames + ['Year(%)']
                                           ] +
                                           [
                                               {
                                                   'if': {
                                                       'filter_query': '{'+col+'} < 0',
                                                       'column_id': ''+col+''
                                                   },
                                                   'backgroundColor': 'indianred'
                                               } for col in monthNames + ['Year(%)']
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
    html.H2('Historically Trending Months'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Month'), width=5, align='left'),
        dbc.Col(html.H6('Select Trend'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='monthly_historicallyTrendingMonthName',
                                   options=monthFullNames,
                                   value='April', multi=False,
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='monthly_historicallyTrendingMonthTrend',
                           inline=True,
                           options=[dict(label='Bullish', value='Bullish'),
                                    dict(label='Bearish', value='Bearish')],
                           value='Bullish',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
    ]),

    html.Br(), html.Br(),
    dbc.Button(id='monthly_historicallyTrendingMonth_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='monthly_historicallyTrendingMonth_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='monthly_historicallyTrendingMonthDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'Year',
                                               },
                                               'backgroundColor': 'lightgrey',
                                               'color': 'black',
                                               'fontWeight': 'bold',
                                               'width': '100px'
                                           }],
                                           style_cell=dict(
                                               whiteSpace='pre-line'
                                           ),
                                           style_table={
                                               'overflowX': 'scroll'
                                           },
                                           style_header=dict(
                                               width='80px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold'
                                           ),
                                           style_data=dict(
                                               width='80px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='white', color='black'
                                           )),],
                     style=dict(width='100%')),
            width=9, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),




    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),

],
    style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)


@callback(
    [
        Output(component_id='monthly_filteredChart', component_property='figure'),
        Output(component_id='monthly_yearlyOverlayChart', component_property='figure'),
        Output(component_id='monthly_aggregateChart', component_property='figure'),
        Output(component_id='monthly_superimposedChart', component_property='figure'),
        Output(component_id='monthly_allDayDataTable', component_property='data'),
        Output(component_id='monthly_typeDataTable', component_property='data'),
        Output(component_id='monthly_yearOnYearReturnsDataTable', component_property='data'),
        Output(component_id='monthly_historicallyTrendingMonthDataTable', component_property='data'),
    ],
    [
        Input('monthly_monthType', 'value'),
        Input('monthly_symbolNameToPlot', 'value'), Input('monthly_dataRange', 'start_date'), Input('monthly_dataRange', 'end_date'), Input('monthly_chartScaleType', 'value'),
        Input('monthly_positiveNegativeYears', 'value'), Input('monthly_evenOddYears', 'value'),
        Input('monthly_positiveNegativeMonths', 'value'), Input('monthly_evenOddMonths', 'value'), Input('monthly_specificMonthSelection', 'value'),
        Input('monthly_monthlyPercentageChange', 'value'), Input('monthly_monthlyPercentageChangeSwitch', 'on'),
        Input('monthly_yearlyPercentageChange', 'value'), Input('monthly_yearlyPercentageChangeSwitch', 'on'),
        Input('monthly_aggregateChartType', 'value'),
        Input('monthly_historicallyTrendingMonthName', 'value'), Input('monthly_historicallyTrendingMonthTrend', 'value'),
    ]
)
def display_monthly(
    monthTypeValue,
    symbolNameToPlotValue, startDate, endDate, chartScaleValue,
    positiveNegativeYearFilter, evenOddYearFilter,
    positiveNegativeMonthFilter, evenOddMonthFilter, specificMonthSelectionValue,
    monthlyPercentageChangeFilter, monthlyPercentageChangeFilterSwitch,
    yearlyPercentageChangeFilter, yearlyPercentageChangeFilterSwitch,
    aggregateChartTypeValue,
    historicallyTrendingMonthName, historicallyTrendingMonthTrend
):

    df = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/' + monthTypeValue + '.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df = df.dropna()
    initialDates = df.copy(deep=True)['Date']

    # choose date range
    df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)]
    historicTrendDayData = df.copy(deep=True)

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

    # add more columns in dataframe
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    # outlier filters
    if (monthlyPercentageChangeFilterSwitch):
        df = df[
            (df['ReturnPercentage'] >= monthlyPercentageChangeFilter[0]) &
            (df['ReturnPercentage'] <= monthlyPercentageChangeFilter[1])
        ]
    if (yearlyPercentageChangeFilterSwitch):
        df = df[
            (df['YearlyReturnPercentage'] >= yearlyPercentageChangeFilter[0]) &
            (df['YearlyReturnPercentage'] <= yearlyPercentageChangeFilter[1])
        ]
    
    # all return figures
    monthlyFilteredChart = go.Figure()
    monthlyYearlyOverlayChart = go.Figure()
    monthlyAggregateChart = go.Figure()
    monthlySuperimposedChart = go.Figure()

    # all return data tables
    monthlyAllDayDataTable = pd.DataFrame()
    monthlyAllDayDataTableReturnPlot = monthlyAllDayDataTable.to_dict('records')
    monthlyDataTable = pd.DataFrame()
    monthlyDataTableReturnPlot = monthlyDataTable.to_dict('records')
    monthlyYearOnYearReturnsDataTable = pd.DataFrame()
    monthlyYearOnYearReturnsDataTableReturnPlot = monthlyYearOnYearReturnsDataTable.to_dict('records')
    historicallyTrendingMonthsDataTable = pd.DataFrame()
    historicallyTrendingMonthsDataTableReturnPlot = historicallyTrendingMonthsDataTable.to_dict('records')

    global monthlyAllDayDataTableDownload
    global monthlyDataTableDownload
    global monthlyYearOnYearReturnsDataTableDownload
    global historicallyTrendingMonthsDataTableDownload

    if (len(df) > 0):

        # create holidays date list only for monthly time frame
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
            plot candle sticks filtered chart for monthly only
        """

        returnPercentageList = df['ReturnPercentage'].to_list()
        returnPointsList = df['ReturnPoints'].to_list()
        hoverExtraTextMessageFilteredChart = [
            'change: ' + f'{returnPointsList[i]:.2f}' + ', ' + f'{returnPercentageList[i]:.2f}' + '%'
            for i in range(len(returnPercentageList))
        ]

        monthlyFilteredChart.add_candlestick(
            x=df['Date'],
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            text=hoverExtraTextMessageFilteredChart
        )

        # update chart layout, axis and remove holidays from chart
        monthlyFilteredChart.update_xaxes(
            rangeslider_visible=False,
            rangebreaks=[],
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False,  dtick = "M48" if evenOddYearFilter!=False else 'M36'
        )
        monthlyFilteredChart.update_yaxes(
            type=chartScaleValue,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        monthlyFilteredChart.update_layout(
            title='Filtered Monthly Chart',
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
            yearly overlay chart for monthly only
        """

        allYearsListInData = sorted(list(set(df['Year'])))

        for i in range(0, len(allYearsListInData)):
            yearRotationalData = df[df['Year'] == allYearsListInData[i]]
            monthlyYearlyOverlayChart.add_scatter(
                x=yearRotationalData['Month'],
                y=yearRotationalData['ReturnPercentage'],
                name=allYearsListInData[i]
            )

        monthlyYearlyOverlayChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        monthlyYearlyOverlayChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        monthlyYearlyOverlayChart.update_layout(
            title='Yearly Overlay Monthly Chart',
            xaxis_title='Months', xaxis_tickformat='%d-%b(%a)<br>%Y',
            yaxis_title='Percentage Change', yaxis_tickformat='.2f',
            legend_title='Years',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        monthlyYearlyOverlayChart.add_hline(y=0, line_width=1, line_dash='solid', line_color='black')

        """
            aggregate chart for monthly only
        """

        aggregateDataFrame = pd.DataFrame()

        if (aggregateChartTypeValue == 'total'):
            aggregateDataFrame = df.groupby('Month')['ReturnPercentage'].sum().reset_index()
        elif (aggregateChartTypeValue == 'average'):
            aggregateDataFrame = df.groupby('Month')['ReturnPercentage'].mean().reset_index()
        elif (aggregateChartTypeValue == 'maximum'):
            aggregateDataFrame = df.groupby('Month')['ReturnPercentage'].max().reset_index()
        elif (aggregateChartTypeValue == 'minimum'):
            aggregateDataFrame = df.groupby('Month')['ReturnPercentage'].min().reset_index()

        monthlyAggregateChart.add_bar(
            x=aggregateDataFrame['Month'],
            y=aggregateDataFrame['ReturnPercentage'],
            marker=dict(color=np.where(aggregateDataFrame['ReturnPercentage'] < 0, 'red', 'green'))
        )
        monthlyAggregateChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        monthlyAggregateChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        monthlyAggregateChart.update_layout(
            title='Aggregate Monthly Chart',
            xaxis_title='Months',
            yaxis_title='Percentage Change', yaxis_tickformat='.2f',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        monthlyAggregateChart.add_hline(y=0, line_width=1, line_dash='solid', line_color='grey')

        """
            super imposed chart for monthly only
        """

        returnsAggregate = pd.DataFrame()
        hoverTextChange = '    YTD '

        returnsAggregate = df.groupby('Month')['ReturnPercentage'].mean().reset_index()
        returnsList = ((returnsAggregate['ReturnPercentage']/100)+1).to_list()

        compoundedReturnsList = [0] * len(returnsList)
        compoundedReturnsList[0] = returnsList[0]

        for i in range(1, len(returnsList)):
            compoundedReturnsList[i] = compoundedReturnsList[i-1]*returnsList[i]

        returnsAggregate['SuperImposedReturn'] = compoundedReturnsList
        returnsAggregate['SuperImposedReturn'] = (returnsAggregate['SuperImposedReturn']-1)*100
        superImposedReturnList = returnsAggregate['SuperImposedReturn'].to_list()

        hoverExtraTextMessageSuperimposedChart = returnsAggregate['ReturnPercentage'].to_list()
        xAxisList = returnsAggregate['Month'].to_list()
        hoverExtraTextMessageSuperimposedChart = [
            f'{(xAxisList[i])}' + '<br>' +
            hoverTextChange + 'Return: ' + f'{superImposedReturnList[i]:.2f}' + '%<br>' +
            'Monthly Change: ' + f'{hoverExtraTextMessageSuperimposedChart[i]:.2f}' + '%'
            for i in range(len(hoverExtraTextMessageSuperimposedChart))
        ]

        monthlySuperimposedChart.add_scatter(
            x=returnsAggregate['Month'],
            y=returnsAggregate['SuperImposedReturn'],
            text=hoverExtraTextMessageSuperimposedChart,
            hoverinfo='text',
            line=dict(color='black')
        )
        monthlySuperimposedChart.update_xaxes(
            rangeslider_visible=False,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        monthlySuperimposedChart.update_yaxes(
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        monthlySuperimposedChart.update_layout(
            title='Superimposed Monthly Chart',
            xaxis_title='Months',
            yaxis_title='Compounded Percentage Return', yaxis_tickformat='.2f',
            hovermode='x unified', hoverdistance=100,
            font=dict(
                family='Courier New, blue',
                size=15,
                color='RebeccaPurple'
            )
        )
        monthlySuperimposedChart.add_hline(y=0, line_width=2, line_dash='solid', line_color='grey')

        """
            dataTable calculation
        """
        allDayReturnPoints = np.array(df['ReturnPercentage'].to_list())

        allDaysStats = getDataTableStatistics(allDayReturnPoints)
        allDayDataTable = pd.concat([monthlyAllDayDataTable, allDaysStats], axis=1)
        allDayDataTable.columns = ['All Months']
        monthlyAllDayDataTableReturnValue = getDataTableForPlot(allDayDataTable)
        monthlyAllDayDataTableReturnPlot = monthlyAllDayDataTableReturnValue[0]
        monthlyAllDayDataTableDownload = dcc.send_data_frame(monthlyAllDayDataTableReturnValue[1].to_csv, 'Youngturtle_All_Months.csv')

        dataTableColumns = []
        dataTableColumns.extend(range(int(min(df['Month'])), int(max(df['Month'])+1), 1))

        for dayName in dataTableColumns:
            dayReturnPoints = np.array(df[df['Month'] == dayName]['ReturnPercentage'].to_list())
            dayStats = getDataTableStatistics(dayReturnPoints)
            monthlyDataTable = pd.concat([monthlyDataTable, dayStats], axis=1)

        monthlyDataTable.columns = dataTableColumns
        monthlyDataTableReturnValue = getDataTableForPlot(monthlyDataTable)
        monthlyDataTableReturnPlot = monthlyDataTableReturnValue[0]
        monthlyDataTableDownload = dcc.send_data_frame(monthlyDataTableReturnValue[1].to_csv, 'Youngturtle_Individual_Months.csv')

        yearOnYearReturnsList = [[] for i in range(len(df['Year'].unique()))]
        yearIndex = -1

        for yearNumber in (df['Year'].unique()):
            yearIndex = yearIndex + 1
            monthIndex = -1
            yearOnYearReturnsList[yearIndex].append(yearNumber)
            InitValue = 100
            for monthNumber in range(1, 13):
                monthIndex = monthIndex + 1
                monthlyReturnList = (df[(df['Year'] == yearNumber) & (df['Month'] == monthNumber)]['ReturnPercentage']).to_list()
                if (len(monthlyReturnList) > 0):
                    InitValue = InitValue*(1+(monthlyReturnList[0]/100))    
                    yearOnYearReturnsList[yearIndex].append(monthlyReturnList[0])
                else:
                    yearOnYearReturnsList[yearIndex].append(np.nan)
            yearOnYearReturnsList[yearIndex].append( round(( (InitValue/100)-1)*100 ,2) )

        monthlyYearOnYearReturnsDataTable = pd.DataFrame(yearOnYearReturnsList)
        monthlyYearOnYearReturnsDataTable.columns = ['Year'] + monthNames + ['Year(%)']
        monthlyYearOnYearReturnsDataTable.fillna(0)
        
        # Average Calculations
        avgNewRow = pd.DataFrame(monthlyYearOnYearReturnsDataTable.mean().round(2)).transpose()
        avgNewRow['Year'] = 'All Average'
        
        posAvgNewRow = pd.DataFrame(monthlyYearOnYearReturnsDataTable[monthlyYearOnYearReturnsDataTable>0].mean().round(2)).transpose()
        posAvgNewRow['Year'] = 'Positive Average'
        
        negAvgNewRow = pd.DataFrame(monthlyYearOnYearReturnsDataTable[monthlyYearOnYearReturnsDataTable<0].mean().round(2)).transpose()
        negAvgNewRow['Year'] = 'Negative Average'
        
        SumNewRow = pd.DataFrame(monthlyYearOnYearReturnsDataTable.count()).transpose()
        SumNewRow['Year'] = 'All Count'
        
        posSumNewRow = pd.DataFrame(monthlyYearOnYearReturnsDataTable[monthlyYearOnYearReturnsDataTable > 0].count()).transpose()
        posSumNewRow['Year'] = 'Positive Count'
        
        negSumNewRow = pd.DataFrame(monthlyYearOnYearReturnsDataTable[monthlyYearOnYearReturnsDataTable < 0].count()).transpose()
        negSumNewRow['Year'] = 'Negative Count'
        
        monthlyYearOnYearReturnsDataTable = pd.concat([monthlyYearOnYearReturnsDataTable,SumNewRow,posSumNewRow,negSumNewRow,avgNewRow,posAvgNewRow,negAvgNewRow])

        monthlyYearOnYearReturnsDataTableReturnPlot = monthlyYearOnYearReturnsDataTable.to_dict('records')
        
        monthlyYearOnYearReturnsDataTableDownload = dcc.send_data_frame(
            monthlyYearOnYearReturnsDataTable.set_index('Year').to_csv, 'Youngturtle_Individual_Months_Returns.csv'
        )

        """
            Historically Trending Days
        """
        # historicallyTrendingMonthName, historicallyTrendingMonthTrend

        # historicTrendDayData = df.copy(deep=True)
        historicallyTrendingMonthName = getMonthNumber(historicallyTrendingMonthName)
        historicallyTrendingMonthTrendMultiplier = True if historicallyTrendingMonthTrend == 'Bullish' else False
        historicallyTrendingMonthsData = historicTrendDayData[
            (historicTrendDayData['Date'].dt.month == historicallyTrendingMonthName) &
            (historicTrendDayData['PositiveMonth'] == historicallyTrendingMonthTrendMultiplier)
        ][['Date', 'Close', 'ReturnPercentage']]
       
        nextMonthNumber = 12 if ((historicallyTrendingMonthName+1) % 12) == 0 else (historicallyTrendingMonthName+1) % 12
        nextThreeMonthNumber = 12 if ((historicallyTrendingMonthName+3) % 12) == 0 else (historicallyTrendingMonthName+3) % 12
        nextSixMonthNumber = 12 if ((historicallyTrendingMonthName+6) % 12) == 0 else (historicallyTrendingMonthName+6) % 12
        nextTwelveMonthNumber = 12 if ((historicallyTrendingMonthName+12) % 12) == 0 else (historicallyTrendingMonthName+12) % 12

        historicallyTrendingMonthsDataList = []
        columnNames = [
            'Year', monthFullNames[historicallyTrendingMonthName-1], monthFullNames[nextMonthNumber-1],
            monthFullNames[nextMonthNumber-1]+'-'+monthFullNames[nextThreeMonthNumber-1],
            monthFullNames[nextMonthNumber-1]+'-'+monthFullNames[nextSixMonthNumber-1],
            monthFullNames[nextMonthNumber-1]+'-'+monthFullNames[nextTwelveMonthNumber-1]
        ]

        for index, historicallyTrendingMonthData in historicallyTrendingMonthsData.iterrows():
            if(pd.to_datetime(historicallyTrendingMonthData['Date'], format='%Y-%m-%d').year in list(df['Date'].dt.year.unique())):
                historicallyTrendingMonthDate = historicallyTrendingMonthData['Date']
                historicallyTrendingMonthReturn = historicallyTrendingMonthData['ReturnPercentage']
                historicallyTrendingMonthClose = historicallyTrendingMonthData['Close']
                nextMonthDate = historicallyTrendingMonthDate+pd.DateOffset(months=1)
                nextThreeMonthDate = historicallyTrendingMonthDate+pd.DateOffset(months=3)
                nextSixMonthDate = historicallyTrendingMonthDate+pd.DateOffset(months=6)
                nextYearMonthDate = historicallyTrendingMonthDate+pd.DateOffset(months=12)
                nextMonthClose = historicTrendDayData[historicTrendDayData['Date'] == nextMonthDate]['Close'].to_list()
                nextThreeMonthClose = historicTrendDayData[historicTrendDayData['Date'] == nextThreeMonthDate]['Close'].to_list()
                nextSixMonthClose = historicTrendDayData[historicTrendDayData['Date'] == nextSixMonthDate]['Close'].to_list()
                nextYearMonthClose = historicTrendDayData[historicTrendDayData['Date'] == nextYearMonthDate]['Close'].to_list()
    
                if (len(nextMonthClose) == len(nextThreeMonthClose) == len(nextSixMonthClose) == len(nextYearMonthClose) == 1):
                    nextMonthReturn = round(((nextMonthClose[0]*100)/historicallyTrendingMonthClose) - 100, 2)
                    nextThreeMonthReturn = round(((nextThreeMonthClose[0]*100)/historicallyTrendingMonthClose) - 100, 2)
                    nextSixMonthReturn = round(((nextSixMonthClose[0]*100)/historicallyTrendingMonthClose) - 100, 2)
                    nextYearMonthReturn = round(((nextYearMonthClose[0]*100)/historicallyTrendingMonthClose) - 100, 2)
                    dataList = [
                        historicallyTrendingMonthDate.strftime('%Y'), historicallyTrendingMonthReturn,
                        nextMonthReturn, nextThreeMonthReturn, nextSixMonthReturn, nextYearMonthReturn
                    ]
                    historicallyTrendingMonthsDataList = [*historicallyTrendingMonthsDataList, dataList]

        historicallyTrendingMonthsDataTable = pd.DataFrame(historicallyTrendingMonthsDataList, columns=columnNames)
        historicallyTrendingMonthsDataTableReturnPlot = historicallyTrendingMonthsDataTable.to_dict('records')
        historicallyTrendingMonthsDataTableDownload = dcc.send_data_frame(
            historicallyTrendingMonthsDataTable.set_index('Year').to_csv, 'Youngturtle_HistoricallyTrending_Months_Returns.csv'
        )

    return [
        monthlyFilteredChart, monthlyYearlyOverlayChart, monthlyAggregateChart, monthlySuperimposedChart,
        monthlyAllDayDataTableReturnPlot, monthlyDataTableReturnPlot, monthlyYearOnYearReturnsDataTableReturnPlot,
        historicallyTrendingMonthsDataTableReturnPlot
    ]


@callback(
    Output(component_id='monthly_allDayDataTable_download_csv', component_property='data'),
    Input('monthly_allDayDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def allDayDataTable_download_monthly(
    allDayDataTable_download_button
):
    return monthlyAllDayDataTableDownload


@callback(
    Output(component_id='monthly_typeDataTable_download_csv', component_property='data'),
    Input('monthly_typeDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def typeDataTable_download_monthly(
    typeDataTable_download_button
):
    return monthlyDataTableDownload


@callback(
    Output(component_id='monthly_yearOnYearReturnsDataTable_download_csv', component_property='data'),
    Input('monthly_yearOnYearReturnsDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def yearOnYearReturns_download_monthly(
    yearOnYearReturns_download_button
):
    return monthlyYearOnYearReturnsDataTableDownload


@callback(
    Output(component_id='monthly_historicallyTrendingMonth_download_csv', component_property='data'),
    Input('monthly_historicallyTrendingMonth_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def monthly_historicallyTrendingMonth_download_monthly(
    monthly_historicallyTrendingMonth_download_button
):
    return historicallyTrendingMonthsDataTableDownload
