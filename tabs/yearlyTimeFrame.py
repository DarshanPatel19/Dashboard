from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

from helper import symbolNamesToDropdown, getDataTableForPlot, getDataTableStatistics


yearlyAllDayDataTableDownload = pd.DataFrame()


yearlyTimeFrameLayout = html.Div([

    html.Br(), html.Br(),
    html.H2('Filtered Yearly Chart Inputs'),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Year Type'), width=8, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='yearly_yearType',
                           inline=True,
                           options=[dict(label='Expiry Year', value='7_ExpiryYear'),
                                    dict(label='Calender Year', value='5_Yearly')],
                           value='5_Yearly',
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
            html.Div([dcc.Dropdown(id='yearly_symbolNameToPlot',
                                   options=symbolNamesToDropdown,
                                   value='BANKNIFTY',
                                   clearable=False, maxHeight=300,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.DatePickerRange(id='yearly_dataRange',
                                min_date_allowed=date(1970, 1, 1), max_date_allowed=date(2025, 12, 31),
                                start_date=date(2019, 2, 1), end_date=date(2023, 3, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='yearly_chartScaleType',
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
            dcc.RadioItems(id='yearly_positiveNegativeYears',
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
            dcc.RadioItems(id='yearly_evenOddYears',
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
    html.H4('Select Percentage Change Range - To Remove Outliers', style={'color': '#00218fa1'}),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('For Yearly'), width=5, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([daq.BooleanSwitch(id='yearly_yearlyPercentageChangeSwitch',
                                        on=False, color='deepskyblue',
                                        persistence=True, persistence_type='session')],
                     style=dict(width='5%')),
            width=5, align='left'
        )
    ]),
    dbc.Row([

        dbc.Col(
            html.Div([dcc.RangeSlider(id='yearly_yearlyPercentageChange',
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
    html.H2('Filtered Yearly Chart Output'),
    dcc.Graph(id='yearly_filteredChart', style=dict(height='90vh')),


    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Data Tables'),

    html.Br(), html.Br(),
    dbc.Button(id='yearly_allDayDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='yearly_allDayDataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='yearly_allDayDataTable',
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
    html.Hr(style={'border': '1px solid #00218fa1'}),


    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),

],
    style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)


@callback(
    [
        Output(component_id='yearly_filteredChart', component_property='figure'),
        Output(component_id='yearly_allDayDataTable', component_property='data'),
    ],
    [
        Input('yearly_yearType', 'value'),
        Input('yearly_symbolNameToPlot', 'value'), Input('yearly_dataRange', 'start_date'), Input('yearly_dataRange', 'end_date'), Input('yearly_chartScaleType', 'value'),
        Input('yearly_positiveNegativeYears', 'value'), Input('yearly_evenOddYears', 'value'),
        Input('yearly_yearlyPercentageChange', 'value'), Input('yearly_yearlyPercentageChangeSwitch', 'on'),
    ]
)
def display_yearly(
    yearTypeValue,
    symbolNameToPlotValue, startDate, endDate, chartScaleValue,
    positiveNegativeYearFilter, evenOddYearFilter,
    yearlyPercentageChangeFilter, yearlyPercentageChangeFilterSwitch,

):

    df = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/' + yearTypeValue + '.csv')
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

    # add more columns in dataframe
    df['Year'] = df['Date'].dt.year

    # outlier filters
    if (yearlyPercentageChangeFilterSwitch):
        df = df[
            (df['ReturnPercentage'] >= yearlyPercentageChangeFilter[0]) &
            (df['ReturnPercentage'] <= yearlyPercentageChangeFilter[1])
        ]

    # all reuturn figures
    yearlyFilteredChart = go.Figure()

    # all return data tables
    yearlyAllDayDataTable = pd.DataFrame()
    yearlyAllDayDataTableReturnPlot = yearlyAllDayDataTable.to_dict('records')

    global yearlyAllDayDataTableDownload

    if (len(df) > 0):

        # create holidays date list only for yearly time frame
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
            plot candle sticks filtered chart for yearly only
        """

        returnPercentageList = df['ReturnPercentage'].to_list()
        returnPointsList = df['ReturnPoints'].to_list()
        hoverExtraTextMessageFilteredChart = [
            'change: ' + f'{returnPointsList[i]:.2f}' + ', ' + f'{returnPercentageList[i]:.2f}' + '%'
            for i in range(len(returnPercentageList))
        ]

        yearlyFilteredChart.add_candlestick(
            x=df['Date'],
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            text=hoverExtraTextMessageFilteredChart
        )

        # update chart layout, axis and remove holidays from chart
        yearlyFilteredChart.update_xaxes(
            rangeslider_visible=False,
            rangebreaks=[],
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False, dtick ="M48" if evenOddYearFilter!=False else 'M36',
        )
        yearlyFilteredChart.update_yaxes(
            type=chartScaleValue,
            showline=True, linewidth=1, linecolor='grey',
            gridcolor='grey', griddash='dot',
            showspikes=True, spikemode='across', spikesnap='cursor',
            spikecolor='grey', spikethickness=1, spikedash='dash',
            fixedrange=False
        )
        yearlyFilteredChart.update_layout(
            title='Filtered Yearly Chart',
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
            dataTable calculation
        """
        allDayReturnPoints = np.array(df['ReturnPercentage'].to_list())

        allDaysStats = getDataTableStatistics(allDayReturnPoints)
        allDayDataTable = pd.concat([yearlyAllDayDataTable, allDaysStats], axis=1)
        allDayDataTable.columns = ['All Years']
        yearlyAllDayDataTableReturnValue = getDataTableForPlot(allDayDataTable)
        yearlyAllDayDataTableReturnPlot = yearlyAllDayDataTableReturnValue[0]
        yearlyAllDayDataTableDownload = dcc.send_data_frame(yearlyAllDayDataTableReturnValue[1].to_csv, 'Youngturtle_All_Years.csv')

    return [yearlyFilteredChart, yearlyAllDayDataTableReturnPlot]


@callback(
    Output(component_id='yearly_allDayDataTable_download_csv', component_property='data'),
    Input('yearly_allDayDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def allDayDataTable_download_yearly(
    allDayDataTable_download_button
):
    return yearlyAllDayDataTableDownload
