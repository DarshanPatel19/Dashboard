from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os
from itertools import zip_longest

from helper import symbolNamesToDropdown, specialDaysToDropdown, weekDays, tradingDays, calenderDays, getDataTableForPlot, getDataTableStatistics, getNConsecutiveSequanceIndexFromList


allScannerSymbolsDataDownload = pd.DataFrame()


symbolScannerLayout = html.Div([

    html.Br(), html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Symbol'), width=5, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('Select Date Range'), width=5, align='left', style={'color': '#00218fa1'})
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='scanner_symbolNameToPlot',
                                   options=[*['All Symbols'], *symbolNamesToDropdown],
                                   value='All Symbols',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.DatePickerRange(id='scanner_dataRange',
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
            dcc.RadioItems(id='scanner_evenOddYears',
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
            dcc.Slider(id='scanner_specificMonthSelection',
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
            html.Div([dcc.Slider(id='scanner_specificExpiryWeekMonthlySelection',
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
            html.Div([dcc.Slider(id='scanner_specificMondayWeekMonthlySelection',
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
    dbc.Row([
        dbc.Col(html.H6('Select Trend Type'), width=5, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('Select Consecutive Trending Days'), width=5, align='left', style={'color': '#00218fa1'}),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='scanner_trendType',
                           inline=True,
                           options=[dict(label='Bullish', value='Bullish'),
                                    dict(label='Bearish', value='Bearish')],
                           value='Bullish',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='scanner_consecutiveTrendingDays',
                                 min=2, max=10, step=1,
                                 marks={i: {'label': str(i), 'style': {'color': 'black'}} for i in range(2, 11)},
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='top'),
                                 included=False,
                                 value=3,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('A --> Select Minimum Accuracy of Each Day(%)'), width=5, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('B --> Select Minimum/Maximum Total of Average P/L of All Trending Days(%)'), width=5, align='left', style={'color': '#00218fa1'}),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Slider(id='scanner_minimumAccuracyOfEachDay',
                                 min=0, max=100, step=5,
                                 marks={
                                     i: {'label': 'Disable', 'style': {'color': 'red'}} if i == 0
                                     else {'label': str(i), 'style': {'color': 'black'}}
                                     for i in range(0, 105, 10)
                                 },
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='top'),
                                 included=True,
                                 value=60,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='scanner_minimumTotalPnlOfAllTrendingDays',
                                 min=0, max=10, step=0.1,
                                 marks={
                                     i: {'label': 'Disable', 'style': {'color': 'red'}} if i == 0
                                     else {'label': str(i), 'style': {'color': 'black'}}
                                     for i in range(0, 11, 1)
                                 },
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='top'),
                                 included=True,
                                 value=1.5,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('C --> Enter Minimum Sample Size'), width=5, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('D --> Select Minimum/Maximum Average P/L of Each Trending Days(%)'), width=5, align='left', style={'color': '#00218fa1'}),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Input(id='scanner_minimumSampleSize',
                                type='number', value=50,
                                placeholder='Enter Sample Size(Number) or Zero(0) to Disable',
                                style={'width': '450px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-left': '20px', 'padding-top': '15px'}),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Slider(id='scanner_minimumAveragePnlOfEachTrendingDays',
                                 min=0, max=5, step=0.1,
                                 marks={
                                     i: {'label': 'Disable', 'style': {'color': 'red'}} if i == 0
                                     else {'label': str(i), 'style': {'color': 'black'}}
                                     for i in range(0, 6, 1)
                                 },
                                 dots=False, updatemode='drag',
                                 tooltip=dict(always_visible=True, placement='top'),
                                 included=True,
                                 value=0.2,
                                 persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H5('Select Query'), width=5, align='left', style={'color': '#00218fa1'}),
    ]),

    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='scanner_input1',
                                   options=['A', 'B', 'C', 'D'],
                                   value='A', disabled=True,
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='50%')),
            align='center'
        ),
        dbc.Col(
            html.Div([dcc.RadioItems(id='scanner_input12operation',
                                     inline=True,
                                     options=[dict(label='OR', value='OR'),
                                              dict(label='AND', value='AND')],
                                     value='OR',
                                     className='radiobutton-group',
                                     persistence=True, persistence_type='session')],
                     ),
            align='center'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='scanner_input2',
                                   options=['A', 'B', 'C', 'D'],
                                   value='B', disabled=True,
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='50%')),
            align='center'
        ),
        dbc.Col(
            html.Div([dcc.RadioItems(id='scanner_input23operation',
                                     inline=True,
                                     options=[dict(label='OR', value='OR'),
                                              dict(label='AND', value='AND')],
                                     value='OR',
                                     className='radiobutton-group',
                                     persistence=True, persistence_type='session')],
                     ),
            align='center'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='scanner_input3',
                                   options=['A', 'B', 'C', 'D'],
                                   value='C', disabled=True,
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='50%')),
            align='center'
        ),
        dbc.Col(
            html.Div([dcc.RadioItems(id='scanner_input34operation',
                                     inline=True,
                                     options=[dict(label='OR', value='OR'),
                                              dict(label='AND', value='AND')],
                                     value='OR',
                                     className='radiobutton-group',
                                     persistence=True, persistence_type='session')],
                     ),
            align='center'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='scanner_input4',
                                   options=['A', 'B', 'C', 'D'],
                                   value='D', disabled=True,
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='50%')),
            align='center'
        )
    ], style={'width': '80%'}),

    html.Br(),
    dbc.Button(
        id='scanner_run',
        children=[html.I(className='fa fa-search'), 'Run Scanner'],
        color='primary', className='me-1',
        size='lg',
    ),

    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    html.Br(),
    dbc.Button(id='scanner_outputTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='scanner_outputTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='scanner_outputTable',
                                           editable=True, page_size=100,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[{
                                               'if': {
                                                   'column_id': 'Ticker-Trading Day',
                                               },
                                               'minWidth': '15px', 'maxWidth': '15px',
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
            width=11, align='left'
        )
    ]),

    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),

],
    style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)


@callback(
    [
        Output(component_id='scanner_outputTable', component_property='data')
    ],
    [
        Input('scanner_symbolNameToPlot', 'value'), Input('scanner_dataRange', 'start_date'), Input('scanner_dataRange', 'end_date'),
        Input('scanner_evenOddYears', 'value'), Input('scanner_specificMonthSelection', 'value'),
        Input('scanner_specificExpiryWeekMonthlySelection', 'value'), Input('scanner_specificMondayWeekMonthlySelection', 'value'),
        Input('scanner_trendType', 'value'), Input('scanner_consecutiveTrendingDays', 'value'),
        Input('scanner_minimumAccuracyOfEachDay', 'value'), Input('scanner_minimumTotalPnlOfAllTrendingDays', 'value'),
        Input('scanner_minimumSampleSize', 'value'), Input('scanner_minimumAveragePnlOfEachTrendingDays', 'value'),
        Input('scanner_input1', 'value'), Input('scanner_input12operation', 'value'),
        Input('scanner_input2', 'value'), Input('scanner_input23operation', 'value'),
        Input('scanner_input3', 'value'), Input('scanner_input34operation', 'value'),
        Input('scanner_input4', 'value'),
        Input('scanner_run', 'n_clicks'),
    ],
    prevent_initial_call=True
)
def display_symbolScanner(
    symbolNameToPlot, scannerStartDate, scannerEndDate,
    evenOddYearsValue, specificMonthValue,
    specificExpiryWeekMonthlyValue, specificMondayWeekMonthlyValue,
    trendTypeValue, consecutiveTrendingDaysValue,
    minimumAccuracyOfEachDayValue, minimumTotalPnlOfAllTrendingDaysValue,
    minimumSampleSizeValue, minimumAveragePnlOfEachTrendingDaysValue,
    input1Value, input12operationValue,
    input2Value, input23operationValue,
    input3Value, input34operationValue,
    input4Value,
    scanner_runButton
):

    global allScannerSymbolsDataDownload
    dayDataTable = pd.DataFrame()
    tableColumns = [
        'Ticker-Trading Day', 'All Count', 'Average Return of All', 'Sum Return of All',
        'Positive Count', 'Positive Accuracy', 'Average Return of Positive', 'Sum Return of Positive',
        'Negative Count', 'Negative Accuracy', 'Average Return of Negative', 'Sum Return of Negative'
    ]
    zeroValuesTable = [[
        'No Symbols Found', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]]
    allScannerSymbolsData = pd.DataFrame(columns=tableColumns).set_index('Ticker-Trading Day')
    zeroLengthScannerSymbolsData = pd.DataFrame(zeroValuesTable, columns=tableColumns).set_index('Ticker-Trading Day')
    filteredReturnIndexChunks = []
    minimumSampleSizeValue = 0 if type(minimumSampleSizeValue) != int else minimumSampleSizeValue

    if (symbolNameToPlot != 'All Symbols'):
        symbolsToRun = [symbolNameToPlot]
    else:
        symbolsToRun = symbolNamesToDropdown

    """
        Run code only after Run Scanner button pressed
    """
    if (scanner_runButton):
        for symbolName in symbolsToRun:
            df = pd.read_csv('./Symbols/' + symbolName + '/1_Daily.csv')
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

            if (len(df) > 0):

                """
                    dataTable calculation
                """
                dayDataTable = pd.DataFrame()
                dataTableColumns = []
                dataTableColumns.extend(range(int(min(df['TradingMonthDay'])), int(max(df['TradingMonthDay'])+1), 1))

                for dayName in dataTableColumns:
                    dayReturnPoints = np.array(df[df['TradingMonthDay'] == dayName]['ReturnPercentage'].to_list())
                    dayStats = getDataTableStatistics(dayReturnPoints)
                    dayDataTable = pd.concat([dayDataTable, dayStats], axis=1)

                dayDataTable.columns = dataTableColumns
                dayDataTableReturnValue = getDataTableForPlot(dayDataTable)
                dayDataTable = dayDataTableReturnValue[1]

                dayDataTable['Positive Accuracy'] = dayDataTable['Positive Count'].apply(
                    lambda x: float(x.split('(')[1].replace('%)', '')) if type(x) == str else x
                )
                dayDataTable['Positive Count'] = dayDataTable['Positive Count'].apply(
                    lambda x: float(x.split('(')[0]) if type(x) == str else x
                )
                dayDataTable['Negative Accuracy'] = dayDataTable['Negative Count'].apply(
                    lambda x: float(x.split('(')[1].replace('%)', '')) if type(x) == str else x
                )
                dayDataTable['Negative Count'] = dayDataTable['Negative Count'].apply(
                    lambda x: float(x.split('(')[0]) if type(x) == str else x
                )
                dayDataTable = dayDataTable.reindex(columns=tableColumns[1:]).reset_index()
                dayDataTable['index'] = dayDataTable['index'].apply(lambda x: symbolName+'-'+str(x))
                dayDataTable = dayDataTable.rename(columns={'index': 'Ticker-Trading Day'}).set_index('Ticker-Trading Day')

                filteredReturnIndexChunks = getNConsecutiveSequanceIndexFromList(
                    dayDataTable, trendTypeValue, consecutiveTrendingDaysValue,
                    minimumAccuracyOfEachDayValue, minimumTotalPnlOfAllTrendingDaysValue,
                    minimumSampleSizeValue, minimumAveragePnlOfEachTrendingDaysValue,
                    input12operationValue, input23operationValue, input34operationValue
                )

                for filteredReturnIndexChunk in filteredReturnIndexChunks:
                    allScannerSymbolsData = pd.concat(
                        [allScannerSymbolsData, dayDataTable.iloc[filteredReturnIndexChunk[0]:filteredReturnIndexChunk[1]+1, :]], axis=0
                    )

    if (len(allScannerSymbolsData) == 0):
        allScannerSymbolsData = zeroLengthScannerSymbolsData.copy(deep=True)

    allScannerSymbolsDataDownload = dcc.send_data_frame(allScannerSymbolsData.to_csv, 'Youngturtle_ScannedSymbols.csv')

    # return [dayDataTable.reset_index().to_dict('records')]
    return [allScannerSymbolsData.reset_index().to_dict('records')]


@callback(
    Output(component_id='scanner_outputTable_download_csv', component_property='data'),
    Input('scanner_outputTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def scanner_outputTable_download(
    scanner_outputTable_download_button
):
    return allScannerSymbolsDataDownload
