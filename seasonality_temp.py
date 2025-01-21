from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
from itertools import zip_longest
import random
import os, json
from collections import defaultdict

from helper import monthNames,monthDict,hoverElecList,lineStyleElecList,symbolNamesToDropdown, \
    watchListToDropDown, specialDaysToDropdown, monthFullNames, \
    tradingDays, calenderDays, colorDict, \
    getDataTableForPlot, getDataTableStatistics, getMonthNumber, getHistoricTrendingDays, \
    filterDataFrameFromHelper, getTrendingDays, \
    getRecentDayReturnPercentage, getRecentWeekReturnPercentage, getRecentMonthReturnPercentage,\
    getElectionfilterDataFrame,electionInfoDf,MaincolorDict,electionDateList,SecondaryColorList, weekDays

def datatable_settings_multiindex(df, flatten_char = '_'):
    datatable_col_list = []
    levels = df.columns.nlevels
    if levels == 1:
        for i in df.columns:
            datatable_col_list.append({"name": i, "id": i})
    else:
        columns_list = []
        for i in df.columns:
            col_id = flatten_char.join(i)
            datatable_col_list.append({"name": i, "id": col_id})
            columns_list.append(col_id)
        df.columns = columns_list
    datatable_data = df.to_dict('records')
    return datatable_col_list, datatable_data


phenomenaDatatableCombinedDownload1 = pd.DataFrame()
phenomenaDatatableCombinedDownload2 = pd.DataFrame()
phenomenaDatatableFilteredDownload = pd.DataFrame()
monthlyComparisonDatatableDownload = pd.DataFrame()
combinedFinal_df1 = pd.DataFrame()
combinedFinal_df2 = pd.DataFrame()
filtered_df1 = pd.DataFrame()
monthlyComparison_df = pd.DataFrame()

assets_path = os.getcwd() + '/assets'


app = Dash(__name__,
           title='5DPSeasonality',
           assets_folder=assets_path, include_assets_files=True,
           suppress_callback_exceptions=True,
           external_stylesheets=[dbc.themes.LITERA],
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
           )

app.layout = html.Div([

    html.Br(), html.Br(),

    # FILTERED Daily CHART INPUT
    html.H2('Phenomena Daily Chart Inputs'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Symbol'), width=4, align='left'),
        dbc.Col(html.H6('Select Date Range'), width=4, align='left'),   
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='phenomena_symbolNameToPlot',
                                   options=symbolNamesToDropdown,
                                   value='BANKNIFTY',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.DatePickerRange(id='phenomena_dateRange',
                                min_date_allowed=date(1900, 1, 1), max_date_allowed=date(2025, 12, 31),
                                start_date=date(2016, 1, 1), end_date=date(2023, 12, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=4, align='left'
        )
        
    ]),
    html.Br(),
   
    dbc.Row([
        dbc.Col(html.H6('Select Positive/Negative Years'), width=4, align='left'),
        dbc.Col(html.H6('Select Even/Odd/Leap Years'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='phenomena_positiveNegativeYears',
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
            dcc.RadioItems(id='phenomena_evenOddYears',
                           inline=True,
                           options=[dict(label='All Years', value='All'),
                                    dict(label='Even Years only', value = True),
                                    dict(label='Odd Years only', value = False),
                                    dict(label='Leap Years only', value = 2)],
                           value='All',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Month'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='phenomena_monthFilter',
                                   options = monthNames + ['Any'],
                                   value='Any',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
        ),
    ]),
    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),


    html.H4('Phenomena Selection Filters', style={'color': '#00218fa1'}),  
    dbc.Row([
        dbc.Col(html.H5('First Phenomenon'), width=6, align='left'),
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select Days'), width=8, align='left'),
        dbc.Col(html.H6('Select Returns'), width=4, align='left'),
    ]),
    dbc.Row([
       dbc.Col(
            html.Div([dcc.RangeSlider(
                        id='phenomena_selectionFirst',
                        min=1, max=23, step=1,
                        marks = {str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(1, 24, 1)},
                        dots=False, updatemode='drag', allowCross=False,
                        tooltip=dict(always_visible=True, placement='bottom'),
                        value=[2, 13],
                        persistence=True, persistence_type='session')],
                style=dict(width='90%')),
            width=8, align='left'
        ),
       dbc.Col(
            dcc.RadioItems(id='phenomena_selectionFirstReturns',
                           inline=True,
                           options=[dict(label='Any', value=0),
                                    dict(label='Positive', value=1),
                                    dict(label='Negative', value=2)],
                           value=0,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
    ]),
    html.Br(),html.Br(), 

    dbc.Row([
        dbc.Col(html.H5('Second Phenomenon'), width=6, align='left'),
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select Days'), width=8, align='left'),
        dbc.Col(html.H6('Select Returns'), width=4, align='left'),
    ]),
    dbc.Row([
       dbc.Col(
            html.Div([dcc.RangeSlider(id='phenomena_selectionSecond',
                                      min=1, max=23, step=1,
                                      marks = {str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(1,24, 1)},
                                      dots=False, updatemode='drag', allowCross=False,
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      value=[13, 16],
                                      persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=8, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='phenomena_selectionSecondReturns',
                            inline=True,
                            options=[dict(label='Any', value=0),
                                    dict(label='Positive', value=1),
                                    dict(label='Negative', value=2)],
                            value=0,
                            className='radiobutton-group',
                            persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
       
    ]),
    html.Br(), html.Br(),

    dbc.Row([
        dbc.Col(html.H5('Third Phenomenon'), width=6, align='left'),
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select Days'), width=8, align='left'),
        dbc.Col(html.H6('Select Returns'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.RangeSlider(
                        id='phenomena_selectionThird',
                        min=-10, max=10, step=1, 
                        marks = {str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(-10, 11, 1) if h!=0} ,
                        dots=False, updatemode='drag', allowCross=False,
                        tooltip=dict(always_visible=True, placement='bottom'),
                        value=[-5, 2],
                        persistence=True, persistence_type='session')],
                        style=dict(width='90%')),
            width=8, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='phenomena_selectionThirdReturns',
                           inline=True,
                           options=[dict(label='Any', value=0),
                                    dict(label='Positive', value=1),
                                    dict(label='Negative', value=2)],
                           value=0,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
    ]),
    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),

    html.H2('Phenomena Daily Chart Output'),
    html.Br(), html.Br(),
    html.H4('Combined Table'),
    html.Br(),
    html.H6('Return Points'),
    html.Br(),

    dbc.Button(id='phenomena_DataTable_Combined1_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='phenomena_DataTable_Combined1_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='phenomena_DataTable_Combined1',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           fixed_rows={'headers': True},
                                           style_table = {'overflowX': 'auto'},
                                           style_data_conditional=[
                                            {
                                            'if': {
                                                'column_id': 'Date',
                                            },
                                            'backgroundColor': 'lightgrey',
                                            'color': 'black',
                                            'fontWeight': 'bold'
                                            },
                                        ]+[                   
                                            {
                                                'if': {
                                                    'filter_query': '{Date} = "All Count"'
                                                },
                                                'borderTop': '5px solid black'
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
                                        ) 
                        )],style=dict(width='100%')),
            width=12, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.H6('Return Percentage'),
    html.Br(),
    dbc.Button(id='phenomena_DataTable_Combined2_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='phenomena_DataTable_Combined2_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='phenomena_DataTable_Combined2',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           fixed_rows={'headers': True},
                                           style_table = {'overflowX': 'auto'},
                                           style_data_conditional=[
                                            {
                                            'if': {
                                                'column_id': 'Date',
                                            },
                                            'backgroundColor': 'lightgrey',
                                            'color': 'black',
                                            'fontWeight': 'bold'
                                            },
                                        ]+[                   
                                            {
                                                'if': {
                                                    'filter_query': '{Date} = "All Count"'
                                                },
                                                'borderTop': '5px solid black'
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
                                        ) 
                        )],style=dict(width='100%')),
            width=12, align='left'
        )
    ]),
    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Plotting Value'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='phenomena_plotvalue',
                           inline=True,
                           options=[
                                    dict(label='ReturnPoints', value=0),
                                    dict(label='ReturnPercentage', value=1)],
                           value=0,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
    ]),
    dcc.Graph(id='phenomena_filteredChart_1', style=dict(height='90vh')),
    html.Br(),
    dcc.Graph(id='phenomena_filteredChart_2', style=dict(height='90vh')),
    html.Br(), html.Br(),
    html.H4('Filtered Table'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select the Phenomena to Display'), width=6, align='left'),
        dbc.Col(html.H6('Select Value to Display'), width=4, align='left')
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='phenomena_datatable_selection_2',
                            inline=True,
                            options=[
                                    dict(label='First', value=1),
                                    dict(label='Second', value=2),
                                    dict(label='Third', value=3),
                                    dict(label='First+Second', value=4),
                                    dict(label='First+Second+Third', value=5),
                                    dict(label='First+Third', value=6),
                                    dict(label='Second+Third', value=7),
                                    ],
                            value=1,
                            className='radiobutton-group',
                            persistence=True, persistence_type='session'),
            width=6, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='phenomena_datatableFilteredPlotValue',
                           inline=True,
                           options=[
                                    dict(label='ReturnPoints', value=0),
                                    dict(label='ReturnPercentage', value=1)],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
    ]),

    html.Br(),
    dbc.Button(id='phenomena_DataTableFiltered_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='phenomena_DataTableFiltered_download_csv'),
    
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='phenomena_DataTable_Filtered',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           fixed_rows={'headers': True},
                                           style_table = {'overflowX': 'auto'},
                                           style_data_conditional=[
                                            {
                                            'if': {
                                                'column_id': 'Date',
                                            },
                                            'backgroundColor': 'lightgrey',
                                            'color': 'black',
                                            'fontWeight': 'bold'
                                            },
                                        ]+[                   
                                            {
                                                'if': {
                                                    'filter_query': '{Date} = "All Count"'
                                                },
                                                'borderTop': '5px solid black'
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
                                        ) 
                        )],style=dict(width='100%')),
            width=12, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    
    html.H2('Monthly Comparison Input'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select First Phenomenon Month'), width=4, align='left'),
        dbc.Col(html.H6('Select Second Phenomenon Month'), width=4, align='left'),
        dbc.Col(html.H6('Select Third Phenomenon Month'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='phenomena_monthlyComparisonFirstMonth',
                                    options = monthNames,
                                    value='Jun',
                                    clearable=False, maxHeight=200,
                                    persistence=True, persistence_type='session'
                                    )],
                        style=dict(width='70%')),
            width=4, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='phenomena_monthlyComparisonSecondMonth',
                                    options = monthNames,
                                    value='Jul', 
                                    clearable=False, maxHeight=200,
                                    persistence=True, persistence_type='session'
                                    )],
                        style=dict(width='70%')),
            width=4, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='phenomena_monthlyComparisonThirdMonth',
                                    options = monthNames,
                                    value='Aug',
                                    clearable=False, maxHeight=200,
                                    persistence=True, persistence_type='session'
                                    )],
                        style=dict(width='70%')),
            width=4, align='left'
        ),
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Include First'), width=4, align='left'),
        dbc.Col(html.H6('Include Second'), width=4, align='left'),
        dbc.Col(html.H6('Include Third'), width=4, align='left'),
    ]),
    dbc.Row([
         dbc.Col(
            dcc.RadioItems(id='phenomena_monthlyComparisonIncludeFirst',
                           inline=True,
                           options=[dict(label='Include', value=1),
                                    dict(label='Exclude', value=0)],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='phenomena_monthlyComparisonIncludeSecond',
                           inline=True,
                           options=[dict(label='Include', value=1),
                                    dict(label='Exclude', value=0)],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='phenomena_monthlyComparisonIncludeThird',
                           inline=True,
                           options=[dict(label='Include', value=1),
                                    dict(label='Exclude', value=0)],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
    ]),
    html.Br(),
     dbc.Row([
        dbc.Col(html.H6('First Value Type'), width=4, align='left'),
        dbc.Col(html.H6('Second Value Type'), width=4, align='left'),
        dbc.Col(html.H6('Third Value Type'), width=4, align='left'),
    ]),
    dbc.Row([
         dbc.Col(
            dcc.RadioItems(id='phenomena_monthlyComparisonFirstReturnType',
                           inline=True,
                           options=[
                                    dict(label='Positive', value=1),
                                    dict(label='Negative', value=0),
                                    dict(label='Any', value=-1)
                                ],
                           value=-1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='phenomena_monthlyComparisonSecondReturnType',
                           inline=True,
                           options=[dict(label='Positive', value=1),
                                    dict(label='Negative', value=0),
                                    dict(label='Any', value=-1)],
                           value=-1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='phenomena_monthlyComparisonThirdReturnType',
                           inline=True,
                           options=[dict(label='Positive', value=1),
                                    dict(label='Negative', value=0),
                                    dict(label='Any', value=-1)],
                           value=-1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
    ]),
    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2("Monthly Comparsion Output"),
    html.Br(),
    
    dbc.Button(id='phenomena_monthlyComparisonDataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='phenomena_monthtlyComparisonDataTable_download_csv'),
    
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='phenomena_monthlyComparisonDataTable',
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           fixed_rows={'headers': True},
                                           style_table = {'overflowX': 'auto'},
                                           style_data_conditional=[
                                            {
                                            'if': {
                                                'column_id': 'Date',
                                            },
                                            'backgroundColor': 'lightgrey',
                                            'color': 'black',
                                            'fontWeight': 'bold'
                                            },
                                        ]+[                   
                                            {
                                                'if': {
                                                    'filter_query': '{Date} = "All Count"'
                                                },
                                                'borderTop': '5px solid black'
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
                                        ) 
                        )],style=dict(width='100%')),
            width=12, align='left'
        )
    ]),

    html.Br(), html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    # END-----------------

    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
],
    style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)


@app.callback(
    [
        Output(component_id='phenomena_DataTable_Combined1', component_property='data'),
        Output(component_id='phenomena_DataTable_Combined2', component_property='data'),
        Output(component_id='phenomena_DataTable_Filtered', component_property='data'),
        Output(component_id='phenomena_filteredChart_1', component_property='figure'),
        Output(component_id='phenomena_filteredChart_2', component_property='figure'),
    ],
    [
        Input('phenomena_symbolNameToPlot', 'value'), 
        Input('phenomena_dateRange', 'start_date'), 
        Input('phenomena_dateRange', 'end_date'),
        Input('phenomena_positiveNegativeYears', 'value'), 
        Input('phenomena_evenOddYears', 'value'),
        Input('phenomena_monthFilter', 'value'),
        Input('phenomena_selectionFirst', 'value'), 
        Input('phenomena_selectionFirstReturns', 'value'), 
        Input('phenomena_selectionSecond', 'value'),
        Input('phenomena_selectionSecondReturns', 'value'), 
        Input('phenomena_selectionThird', 'value'),
        Input('phenomena_selectionThirdReturns', 'value'), 
        Input('phenomena_datatable_selection_2', 'value'),    
        Input('phenomena_datatableFilteredPlotValue', 'value'),
        Input('phenomena_plotvalue', 'value'),
    ]
)
def display_phenomenaReturns(symbolNameToPlotValue, startDate, endDate, 
    positiveNegativeYearFilter, evenOddYearFilter, monthFilter,
    firstPhenomenaDays, firstPhenomenaReturnsFilter,
    secondPhenomenaDays, secondPhenomenaReturnsFilter,                          
    thirdPhenomenaDays, thirdPhenomenaReturnsFilter,
    datatableFilter_2, datatableFilteredPlotValue, plotvalue
):
    df = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/1_Daily.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
    df = df.dropna()
    df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)]
    
    # choose positive/negative, even/odd years
    if (positiveNegativeYearFilter != 'All'):
        df = df[df['PositiveYear'] == positiveNegativeYearFilter]
    if (evenOddYearFilter != 'All'):
        if(evenOddYearFilter != 2):
            df = df[df['EvenYear'] == evenOddYearFilter]
        else:
            df = df[(df['Date'].dt.year % 4 == 0) & ((df['Date'].dt.year % 100 != 0) | (df['Date'].dt.year % 400 == 0))]
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    
    monthDict = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
    monthDict1 = { 1:'Jan', 2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    
    # Month Filter
    if(monthFilter!='Any'):
        df = df[df['Month']==monthDict[monthFilter]]
    
    #Get specific columns data to be used
    df = df[['Ticker', 'Date', 'Close', 'Month', 'Year', 'TradingMonthDay']].reset_index(drop=True)
    
    if(thirdPhenomenaDays[0]>=0):
        thirdPhenomenaDays[0] = -5
    if(thirdPhenomenaDays[1]<=0):
        thirdPhenomenaDays[1] = 2

    # Combined Table Columns
    columnsToPlot = list()
    columnsToPlot = (
            [f'({days[0]},{days[1] - days[0]})' for days in [firstPhenomenaDays]] +
            [f'({days[0]},{days[1] - days[0]})' for days in [secondPhenomenaDays]] +
            [f'({abs(days[0])},{days[1]})' for days in [thirdPhenomenaDays]]           
        )
    
    # Filtered Table Columns
    columnsToPlot_2 = list()
    if(datatableFilter_2==1 or datatableFilter_2==4 or datatableFilter_2==5 or datatableFilter_2==6):
        columnsToPlot_2 = columnsToPlot_2 + [f'({days[0]},{days[1] - days[0]})' for days in [firstPhenomenaDays]]
    if(datatableFilter_2==2 or datatableFilter_2==4 or datatableFilter_2==5 or datatableFilter_2==7):
        columnsToPlot_2 = columnsToPlot_2 + [f'({days[0]},{days[1] - days[0]})' for days in [secondPhenomenaDays]]
    if(datatableFilter_2==3 or datatableFilter_2==5 or datatableFilter_2==6 or datatableFilter_2==7):
        columnsToPlot_2 = columnsToPlot_2 + [f'({abs(days[0])},{days[1]})' for days in [thirdPhenomenaDays]]           
    
    first_df = df.copy(deep=True)
    second_df = df.copy(deep=True)
    third_df = df.copy(deep=True)
    
    #Initializing variables, dictionaries and dataframes 
    firstReturnDict = defaultdict(lambda: defaultdict(list))  
    secondReturnDict = defaultdict(lambda: defaultdict(list))
    thirdReturnDict = defaultdict(lambda: defaultdict(list)) 
    
    
    
    temp_df = pd.DataFrame()
    yearsList = list(df['Year'].unique())

    # Creating dictionaries for each Phenomena
    if(len(first_df)>0):
        for year in yearsList:
            temp_df = first_df[first_df['Year']==year]
            for month in temp_df['Month'].unique():
                filtered_df = pd.DataFrame()
                filtered_df = first_df[(first_df['TradingMonthDay'] >= firstPhenomenaDays[0]) 
                                        & (first_df['Year']==year)
                                        & (first_df['Month']==month)
                                        & (first_df['TradingMonthDay'] <= firstPhenomenaDays[1])
                            ].reset_index(drop=True)
                if(len(filtered_df) > (firstPhenomenaDays[1]-firstPhenomenaDays[0])):
                    firstClose = filtered_df.iloc[0]['Close']
                    secondClose = filtered_df.iloc[-1]['Close']
                    diff1 = round(secondClose - firstClose,2)
                    diff2 = round((diff1/firstClose)*100,2)
                    firstReturnDict[monthDict1[month] + '-' +str(year)] = [diff1, diff2]
                else:
                    print(f"Date insufficient for First phenomenon for {monthDict1[month]}-{year}")
                
    if(len(second_df)>0):
        for year in yearsList:
            temp_df = second_df[second_df['Year']==year]
            for month in temp_df['Month'].unique():
                filtered_df = pd.DataFrame()
                filtered_df = second_df[(second_df['TradingMonthDay'] >= secondPhenomenaDays[0]) 
                                        & (second_df['Year']==year) 
                                        & (second_df['Month']==month) 
                                        & (second_df['TradingMonthDay'] <= secondPhenomenaDays[1])
                            ].reset_index(drop=True)
                if(len(filtered_df) > (secondPhenomenaDays[1]-secondPhenomenaDays[0])):
                    firstClose = filtered_df.iloc[0]['Close']
                    secondClose = filtered_df.iloc[-1]['Close']
                    diff1 = round(secondClose - firstClose,2)
                    diff2 = round((diff1/firstClose)*100,2)
                    secondReturnDict[monthDict1[month] + '-' +str(year)] = [diff1, diff2]
                else:
                    print(f"Date insufficient for Second phenomenon for {monthDict1[month]}-{year}")

    if(len(third_df)>0):
        for year in yearsList:
            temp_df = third_df[third_df['Year']==year]
            for month in temp_df['Month'].unique():
                filtered_df = pd.DataFrame()
                filtered_df = third_df[(third_df['Year']==year)
                                        & (third_df['Month']==month)
                                        ]
                if(len(filtered_df)>=abs(thirdPhenomenaDays[0])):    
                    firstIndex =  filtered_df.index[thirdPhenomenaDays[0]]
                    firstClose = filtered_df.loc[firstIndex,'Close']
                    secondIndex = firstIndex + abs(thirdPhenomenaDays[0]) + thirdPhenomenaDays[1] -1
                    if(secondIndex <= len(df)):
                        secondClose = df.loc[secondIndex]['Close']
                        diff1 = round(secondClose - firstClose,2)
                        diff2 = round((diff1/firstClose)*100,2)
                        thirdReturnDict[monthDict1[month] + '-' +str(year)] = [diff1, diff2]
                    else:
                        print(f"Date insufficient for third phenomenon for {monthDict1[month]}-{year}")
                else:
                     print(f"Date insufficient for third phenomenon for {monthDict1[month]}-{year}")
    # Get Combined Data
    all_keys = set(firstReturnDict.keys()) | set(secondReturnDict.keys()) | set(thirdReturnDict.keys())
    sorted_all_keys = sorted(all_keys, key=lambda x: (x.split('-')[1], monthDict[x.split('-')[0]]), reverse=False)
    data1 = []
    data2 = []

    for key in sorted_all_keys:
        row_data1 = {}
        row_data2 = {}
        for phenomena in columnsToPlot:
            value1, value2 = None, None
            if phenomena == columnsToPlot[0] and key in firstReturnDict:
                value1,value2 = firstReturnDict[key]
            elif phenomena == columnsToPlot[1] and key in secondReturnDict:
                value1,value2 = secondReturnDict[key]
            elif phenomena == columnsToPlot[2] and key in thirdReturnDict:
                value1,value2 = thirdReturnDict[key]
            row_data1['Date'] = key
            row_data1[phenomena] = value1
            row_data2['Date'] = key
            row_data2[phenomena] = value2
        data1.append(row_data1)
        data2.append(row_data2)
    
    # Return Tables and Figures
    global combinedFinal_df1 
    global combinedFinal_df2 
    global filtered_df1
    global phenomenaDatatableCombinedDownload1
    global phenomenaDatatableCombinedDownload2
    global phenomenaDatatableFilteredDownload
    dfpheomenaChart = pd.DataFrame()
    combinedFinal_df1Plot = combinedFinal_df1.to_dict('records')
    combinedFinal_df2Plot = combinedFinal_df2.to_dict('records')
    filtered_dfPlot = filtered_df1.to_dict('records')

    pheomenaChart_2 = go.Figure()
    pheomenaChart_1 = go.Figure()

    # Create Combined and Filtered Table
    if len(data1) > 0:
        combinedFinal_df1 = pd.DataFrame(data1)
        combinedFinal_df2 = pd.DataFrame(data2)
        if(datatableFilteredPlotValue==0):
            filtered_df1 = combinedFinal_df1.copy(deep=True)
        else:
            filtered_df1 = combinedFinal_df2.copy(deep=True)

        allReturnColumns = combinedFinal_df1.columns
        combinedFinal_df1['Total'] = combinedFinal_df1[allReturnColumns[1:]].sum(axis=1).round(2)
        combinedFinal_df2['Total'] = combinedFinal_df2[allReturnColumns[1:]].sum(axis=1).round(2)
        
        for column in allReturnColumns[1:]:
            combinedFinal_df1[column+'%'] = ((combinedFinal_df1[column]/abs(combinedFinal_df1['Total']))*100).round(2)
            combinedFinal_df2[column+'%'] = ((combinedFinal_df2[column]/abs(combinedFinal_df2['Total']))*100).round(2)
        
        totalCount = [combinedFinal_df1[colName].count() for colName in allReturnColumns[1:]]
        averageReturns = [round(i, 2) for i in combinedFinal_df1[allReturnColumns[1:]].mean()]
        totalSum = [round(i, 2) for i in combinedFinal_df1[allReturnColumns[1:]].sum()]
        positiveCount = [combinedFinal_df1[colName][combinedFinal_df1[colName] > 0].count() for colName in allReturnColumns[1:]]
        positiveMean = [round(combinedFinal_df1[colName][combinedFinal_df1[colName] > 0].mean(), 2) for colName in allReturnColumns[1:]]
        positiveSum = [round(combinedFinal_df1[colName][combinedFinal_df1[colName] > 0].sum(), 2) for colName in allReturnColumns[1:]]
        negativeCount = [combinedFinal_df1[colName][combinedFinal_df1[colName] < 0].count() for colName in allReturnColumns[1:]]
        negativeMean = [round(combinedFinal_df1[colName][combinedFinal_df1[colName] < 0].mean(), 2) for colName in allReturnColumns[1:]]
        negativeSum = [round(combinedFinal_df1[colName][combinedFinal_df1[colName] < 0].sum(), 2) for colName in allReturnColumns[1:]]
        
        combinedFinal_df1 = pd.concat([combinedFinal_df1,  pd.DataFrame({value: [[*['All Count'], *totalCount][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df1 = pd.concat([combinedFinal_df1,  pd.DataFrame({value: [[*['Pos Count'], *positiveCount][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df1 = pd.concat([combinedFinal_df1,  pd.DataFrame({value: [[*['Neg Count'], *negativeCount][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df1 = pd.concat([combinedFinal_df1,  pd.DataFrame({value: [[*['Avg Return All'], *averageReturns][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df1 = pd.concat([combinedFinal_df1,  pd.DataFrame({value: [[*['Avg Return Pos'], *positiveMean][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df1 = pd.concat([combinedFinal_df1,  pd.DataFrame({value: [[*['Avg Return Neg'], *negativeMean][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df1 = pd.concat([combinedFinal_df1,  pd.DataFrame({value: [[*['Sum Return All'], *totalSum][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df1 = pd.concat([combinedFinal_df1,  pd.DataFrame({value: [[*['Sum Return Pos'], *positiveSum][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df1 = pd.concat([combinedFinal_df1,  pd.DataFrame({value: [[*['Sum Return Neg'], *negativeSum][i]] for i, value in enumerate(allReturnColumns)})])
    
        dfpheomenaChart['Phenomena'] = columnsToPlot
        if(plotvalue==0):
            dfpheomenaChart['Returns'] = averageReturns
            title_chart = 'Phenomena Average Returns Points'

        totalCount = [combinedFinal_df2[colName].count() for colName in allReturnColumns[1:]]
        averageReturns = [round(i, 2) for i in combinedFinal_df2[allReturnColumns[1:]].mean()]
        totalSum = [round(i, 2) for i in combinedFinal_df2[allReturnColumns[1:]].sum()]
        positiveCount = [combinedFinal_df2[colName][combinedFinal_df2[colName] > 0].count() for colName in allReturnColumns[1:]]
        positiveMean = [round(combinedFinal_df2[colName][combinedFinal_df2[colName] > 0].mean(), 2) for colName in allReturnColumns[1:]]
        positiveSum = [round(combinedFinal_df2[colName][combinedFinal_df2[colName] > 0].sum(), 2) for colName in allReturnColumns[1:]]
        negativeCount = [combinedFinal_df2[colName][combinedFinal_df2[colName] < 0].count() for colName in allReturnColumns[1:]]
        negativeMean = [round(combinedFinal_df2[colName][combinedFinal_df2[colName] < 0].mean(), 2) for colName in allReturnColumns[1:]]
        negativeSum = [round(combinedFinal_df2[colName][combinedFinal_df2[colName] < 0].sum(), 2) for colName in allReturnColumns[1:]]
        
        combinedFinal_df2 = pd.concat([combinedFinal_df2,  pd.DataFrame({value: [[*['All Count'], *totalCount][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df2 = pd.concat([combinedFinal_df2,  pd.DataFrame({value: [[*['Pos Count'], *positiveCount][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df2 = pd.concat([combinedFinal_df2,  pd.DataFrame({value: [[*['Neg Count'], *negativeCount][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df2 = pd.concat([combinedFinal_df2,  pd.DataFrame({value: [[*['Avg Return All'], *averageReturns][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df2 = pd.concat([combinedFinal_df2,  pd.DataFrame({value: [[*['Avg Return Pos'], *positiveMean][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df2 = pd.concat([combinedFinal_df2,  pd.DataFrame({value: [[*['Avg Return Neg'], *negativeMean][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df2 = pd.concat([combinedFinal_df2,  pd.DataFrame({value: [[*['Sum Return All'], *totalSum][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df2 = pd.concat([combinedFinal_df2,  pd.DataFrame({value: [[*['Sum Return Pos'], *positiveSum][i]] for i, value in enumerate(allReturnColumns)})])
        combinedFinal_df2 = pd.concat([combinedFinal_df2,  pd.DataFrame({value: [[*['Sum Return Neg'], *negativeSum][i]] for i, value in enumerate(allReturnColumns)})])
        
        phenomenaDatatableCombinedDownload1 = dcc.send_data_frame(combinedFinal_df1.set_index('Date').to_csv, 'Youngturtle_PhenomenaReturns.csv')
        phenomenaDatatableCombinedDownload2 = dcc.send_data_frame(combinedFinal_df2.set_index('Date').to_csv, 'Youngturtle_PhenomenaReturns.csv')
        combinedFinal_df1Plot = combinedFinal_df1.to_dict('records')
        combinedFinal_df2Plot = combinedFinal_df2.to_dict('records')

        if(plotvalue==1):
            dfpheomenaChart['Returns'] = averageReturns
            title_chart = 'Phenomena Average Returns Percentage'

        for index, row in dfpheomenaChart.iterrows():
            pheomenaChart_1.add_trace(go.Scatter(
                x=[row['Phenomena']], 
                y=[row['Returns']],  
                mode='markers', 
                name=str(row['Returns']), 
                text=[row['Phenomena'] + ': ' + str(row['Returns'])], 
                hoverinfo='text ',  
            ))
            pheomenaChart_1.add_trace(go.Scatter(
                x=[row['Phenomena'], dfpheomenaChart.loc[0]['Phenomena']], 
                y=[row['Returns'], 0],  
                mode='lines+markers',
                showlegend=False, 
                hoverinfo = 'skip',
            ))
       
        pheomenaChart_1.update_layout(
            title=title_chart,
            xaxis_title='Phenomena',
            yaxis_title='Returns',
            yaxis_tickformat='.2f',
            hovermode = 'x unified',
            hoverdistance = 100,
            font=dict(
                family='Courier New, blue',
                size=15,
            color='RebeccaPurple'
            ),
            showlegend=False,
        )
        
        pheomenaChart_2 = go.Figure(data=[go.Bar(x=dfpheomenaChart['Phenomena'], y=dfpheomenaChart['Returns'])])
        pheomenaChart_2.update_layout(
            title =title_chart,
            xaxis_title='Phenomena',
            yaxis_title='Returns',
            yaxis_tickformat='.2f',
            hovermode = 'x unified',
            hoverdistance = 100,
            font=dict(
                family='Courier New, blue',
                size=15,
            color='RebeccaPurple'
            ),
            showlegend=False,
        )
        
   
    if(len(filtered_df1)>0):
        for column in columnsToPlot:
            if(column==columnsToPlot[0]):
                if(firstPhenomenaReturnsFilter==1):
                    filtered_df1[column] = filtered_df1[filtered_df1[column]>0][column]
                elif(firstPhenomenaReturnsFilter==2):
                    filtered_df1[column] = filtered_df1[filtered_df1[column]<0][column]
                    
            elif(column==columnsToPlot[1]):
                if(secondPhenomenaReturnsFilter==1):
                    filtered_df1[column] = filtered_df1[filtered_df1[column]>0][column]
                elif(secondPhenomenaReturnsFilter==2):
                    filtered_df1[column] = filtered_df1[filtered_df1[column]<0][column]

            elif(column==columnsToPlot[2]):
                if(thirdPhenomenaReturnsFilter==1):
                   filtered_df1[column] = filtered_df1[filtered_df1[column]>0][column]
                elif(thirdPhenomenaReturnsFilter==2):
                    filtered_df1[column] = filtered_df1[filtered_df1[column]<0][column]       
        
        filtered_df1 = filtered_df1.dropna(how='any')    
        finalcolumns = ['Date'] + columnsToPlot_2
        filtered_df1 = filtered_df1[[column for column in filtered_df1.columns if column in finalcolumns]] 
        allReturnColumns = filtered_df1.columns
        
        totalCount = [filtered_df1[colName].count() for colName in allReturnColumns[1:]]
        averageReturns = [round(i, 2) for i in filtered_df1[allReturnColumns[1:]].mean()]
        totalSum = [round(i, 2) for i in filtered_df1[allReturnColumns[1:]].sum()]
        positiveCount = [filtered_df1[colName][filtered_df1[colName] > 0].count() for colName in allReturnColumns[1:]]
        positiveMean = [round(filtered_df1[colName][filtered_df1[colName] > 0].mean(), 2) for colName in allReturnColumns[1:]]
        positiveSum = [round(filtered_df1[colName][filtered_df1[colName] > 0].sum(), 2) for colName in allReturnColumns[1:]]
        negativeCount = [filtered_df1[colName][filtered_df1[colName] < 0].count() for colName in allReturnColumns[1:]]
        negativeMean = [round(filtered_df1[colName][filtered_df1[colName] < 0].mean(), 2) for colName in allReturnColumns[1:]]
        negativeSum = [round(filtered_df1[colName][filtered_df1[colName] < 0].sum(), 2) for colName in allReturnColumns[1:]]
        
        filtered_df1 = pd.concat([filtered_df1,  pd.DataFrame({value: [[*['All Count'], *totalCount][i]] for i, value in enumerate(allReturnColumns)})])
        filtered_df1 = pd.concat([filtered_df1,  pd.DataFrame({value: [[*['Pos Count'], *positiveCount][i]] for i, value in enumerate(allReturnColumns)})])
        filtered_df1 = pd.concat([filtered_df1,  pd.DataFrame({value: [[*['Neg Count'], *negativeCount][i]] for i, value in enumerate(allReturnColumns)})])
        filtered_df1 = pd.concat([filtered_df1,  pd.DataFrame({value: [[*['Avg Return All'], *averageReturns][i]] for i, value in enumerate(allReturnColumns)})])
        filtered_df1 = pd.concat([filtered_df1,  pd.DataFrame({value: [[*['Avg Return Pos'], *positiveMean][i]] for i, value in enumerate(allReturnColumns)})])
        filtered_df1 = pd.concat([filtered_df1,  pd.DataFrame({value: [[*['Avg Return Neg'], *negativeMean][i]] for i, value in enumerate(allReturnColumns)})])
        filtered_df1 = pd.concat([filtered_df1,  pd.DataFrame({value: [[*['Sum Return All'], *totalSum][i]] for i, value in enumerate(allReturnColumns)})])
        filtered_df1 = pd.concat([filtered_df1,  pd.DataFrame({value: [[*['Sum Return Pos'], *positiveSum][i]] for i, value in enumerate(allReturnColumns)})])
        filtered_df1 = pd.concat([filtered_df1,  pd.DataFrame({value: [[*['Sum Return Neg'], *negativeSum][i]] for i, value in enumerate(allReturnColumns)})])
        filtered_df1 = filtered_df1.fillna(0)
        filtered_dfPlot = filtered_df1.to_dict('records')
        phenomenaDatatableFilteredDownload = dcc.send_data_frame(filtered_df1.set_index('Date').to_csv, 'Youngturtle_PhenomenaFilteredReturns.csv')
        
    return [
        combinedFinal_df1Plot,
        combinedFinal_df2Plot,
        filtered_dfPlot,
        pheomenaChart_1,
        pheomenaChart_2,
    ]

# @app.callback(
#     Output('phenomena_DataTable_Combined1', 'style_data_conditional'),
#     Input('phenomena_DataTable_Combined1', 'data')
# )
# def update_datatable(data):
#     global combinedFinal_df1
#     columns = combinedFinal_df1.columns
#     summary_reports = ["All Count", "Pos Count", "Neg Count", "Avg Return All", "Avg Return Pos", "Avg Return Neg", "Sum Return All", "Sum Return Pos", "Sum Return Neg"]

#     style_data_conditional = [
#             {
#                 'if': {
#                 'filter_query': '{{{}}} > 0'.format(col),
#                 'column_id': col
#             },
#             'backgroundColor': 'green'
#         } for col in columns if col != 'Date'
#         ]+[
#             {
#                 'if': {
#                     'filter_query': '{{{}}} < 0'.format(col),
#                     'column_id': col
#                 },
#                 'backgroundColor': 'red'
#             } for col in columns if col != 'Date'
#         ]+[

#         ]+[
#             {
#             'if': {
#                 'column_id': 'Date',
#             },
#             'backgroundColor': 'lightgrey',
#             'color': 'black',
#             'fontWeight': 'bold'
#             },
#         ]+[                   
#             {
#                 'if': {
#                     'filter_query': '{Date} = "All Count"'
#                 },
#                 'borderTop': '5px solid black'
#             }
#         ]
#     return  style_data_conditional

# @app.callback(
#     Output('phenomena_DataTable_Combined2', 'style_data_conditional'),
#     Input('phenomena_DataTable_Combined2', 'data')
# )
# def update_datatable(data):
#     global combinedFinal_df2
#     columns = combinedFinal_df2.columns
#     summary_reports = ["All Count", "Pos Count", "Neg Count", "Avg Return All", "Avg Return Pos", "Avg Return Neg", "Sum Return All", "Sum Return Pos", "Sum Return Neg"]

#     style_data_conditional = [
#             {
#                 'if': {
#                 'filter_query': '{{{}}} > 0'.format(col),
#                 'column_id': col
#             },
#             'backgroundColor': 'green'
#         } for col in columns if col != 'Date'
#         ]+[
#             {
#                 'if': {
#                     'filter_query': '{{{}}} < 0'.format(col),
#                     'column_id': col
#                 },
#                 'backgroundColor': 'red'
#             } for col in columns if col != 'Date'
#         ]+[
#             {
#             'if': {
#                 'column_id': 'Date',
#             },
#             'backgroundColor': 'lightgrey',
#             'color': 'black',
#             'fontWeight': 'bold'
#             },
#         ]+[                   
#             {
#                 'if': {
#                     'filter_query': '{Date} = "All Count"'
#                 },
#                 'borderTop': '5px solid black'
#             }
#         ]
#     return  style_data_conditional

# @app.callback(
#     Output('phenomena_DataTable_Filtered', 'style_data_conditional'),
#     Input('phenomena_DataTable_Filtered', 'data')
# )
# def update_datatable(data):
#     global filtered_df1
#     columns = filtered_df1.columns
#     summary_reports = ["All Count", "Pos Count", "Neg Count", "Avg Return All", "Avg Return Pos", "Avg Return Neg", "Sum Return All", "Sum Return Pos", "Sum Return Neg"]

#     style_data_conditional = [
#             {
#                 'if': {
#                 'filter_query': '{{{}}} > 0'.format(col),
#                 'column_id': col
#             },
#             'backgroundColor': 'green'
#         } for col in columns if col != 'Date'
#         ]+[
#             {
#                 'if': {
#                     'filter_query': '{{{}}} < 0'.format(col),
#                     'column_id': col
#                 },
#                 'backgroundColor': 'red'
#             } for col in columns if col != 'Date'
#         ]+[
#             {
#             'if': {
#                 'column_id': 'Date',
#             },
#             'backgroundColor': 'lightgrey',
#             'color': 'black',
#             'fontWeight': 'bold'
#             },
#         ]+[                   
#             {
#                 'if': {
#                     'filter_query': '{Date} = "All Count"'
#                 },
#                 'borderTop': '5px solid black'
#             }
#         ]
#     return  style_data_conditional

@app.callback(
    Output(component_id='phenomena_monthlyComparisonDataTable', component_property='data'),
    [
        Input('phenomena_symbolNameToPlot', 'value'), 
        Input('phenomena_dateRange', 'start_date'), 
        Input('phenomena_dateRange', 'end_date'),
        Input('phenomena_positiveNegativeYears', 'value'), 
        Input('phenomena_evenOddYears', 'value'),
        Input('phenomena_selectionFirst', 'value'), 
        Input('phenomena_selectionSecond', 'value'),
        Input('phenomena_selectionThird', 'value'),
        Input('phenomena_monthlyComparisonFirstMonth', 'value'),
        Input('phenomena_monthlyComparisonSecondMonth', 'value'),
        Input('phenomena_monthlyComparisonThirdMonth', 'value'),
        Input('phenomena_monthlyComparisonIncludeFirst', 'value'),
        Input('phenomena_monthlyComparisonIncludeSecond', 'value'),
        Input('phenomena_monthlyComparisonIncludeThird', 'value'),
        Input('phenomena_monthlyComparisonFirstReturnType', 'value'),
        Input('phenomena_monthlyComparisonSecondReturnType', 'value'),
        Input('phenomena_monthlyComparisonThirdReturnType', 'value'),
    ]   
)
def displayMonthlyComparisonReturnPercentage(symbolNameToPlotValue, startDate, endDate,
    positiveNegativeYearFilter, evenOddYearFilter, firstPhenomenaDays, secondPhenomenaDays,
    thirdPhenomenaDays, monthlyComparisonFirstMonth, monthlyComparisonSecondMonth,monthlyComparisonThirdMonth,
    monthlyComparisonIncludeFirst, monthlyComparisonIncludeSecond, monthlyComparisonIncludeThird,
    monthlyComparisonFirstReturnType, monthlyComparisonSecondReturnType, monthlyComparisonThirdReturnType 
):
    df = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/1_Daily.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
    df = df.dropna()
    df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)].reset_index(drop=True)
    original_df = df.copy(deep=True)
    
    # choose positive/negative, even/odd years
    if (positiveNegativeYearFilter != 'All'):
        df = df[df['PositiveYear'] == positiveNegativeYearFilter]
    if (evenOddYearFilter != 'All'):
        if(evenOddYearFilter != 2):
            df = df[df['EvenYear'] == evenOddYearFilter]
        else:
            df = df[(df['Date'].dt.year % 4 == 0) & ((df['Date'].dt.year % 100 != 0) | (df['Date'].dt.year % 400 == 0))]
    
    #Create Year and Month Column
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month  
    
    # Dictionaries to use inside 
    monthDict = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
    monthDict1 = { 1:'Jan', 2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    yearsList = list(df['Year'].unique())
    #Get specific columns data to be used
    df = df[['Ticker', 'Date', 'Close', 'Month', 'Year', 'TradingMonthDay']]
    
    # Dealing with exceptions
    if(thirdPhenomenaDays[0]>=0):
        thirdPhenomenaDays[0] = -5
    if(thirdPhenomenaDays[1]<=0):
        thirdPhenomenaDays[1] = 2

    if((monthlyComparisonIncludeFirst +  monthlyComparisonIncludeSecond + monthlyComparisonIncludeThird) == 0):
        monthlyComparisonIncludeFirst = 1
    
    columnsToPlot =  list()
    columnsToPlot1 = (
            [f'({days[0]},{days[1] - days[0]})' for days in [firstPhenomenaDays]] +
            [f'({days[0]},{days[1] - days[0]})' for days in [secondPhenomenaDays]] +
            [f'({abs(days[0])},{days[1]})' for days in [thirdPhenomenaDays]]           
    )
    firstReturnDf = pd.DataFrame()
    secondReturnDf = pd.DataFrame()
    thirdReturnDf = pd.DataFrame()
    firstReturnDict = defaultdict(lambda: defaultdict(list))
    secondReturnDict = defaultdict(lambda: defaultdict(list))
    thirdReturnDict = defaultdict(lambda: defaultdict(list))
   
    
    
    if(monthlyComparisonIncludeFirst):
        columnsToPlot = columnsToPlot + [f'({days[0]},{days[1] - days[0]})' for days in [firstPhenomenaDays]]    
    if(monthlyComparisonIncludeSecond):
        columnsToPlot = columnsToPlot +  [f'({days[0]},{days[1] - days[0]})' for days in [secondPhenomenaDays]]
    if(monthlyComparisonIncludeThird):
        columnsToPlot = columnsToPlot +  [f'({abs(days[0])},{days[1]})' for days in [thirdPhenomenaDays]]           

    first_df = df[df['Month']==monthDict[monthlyComparisonFirstMonth]]
    for year in first_df['Year'].unique():
        filtered_df = first_df[(first_df['TradingMonthDay'] >= firstPhenomenaDays[0]) 
                                & (first_df['Year']==year)
                                & (first_df['TradingMonthDay'] <= firstPhenomenaDays[1])
                        ].reset_index(drop=True)
        if(len(filtered_df) > (firstPhenomenaDays[1]-firstPhenomenaDays[0])):
            firstClose = filtered_df.iloc[0]['Close']
            secondClose = filtered_df.iloc[-1]['Close']
            diff = round(secondClose - firstClose,2)
            diff1 = round((diff/firstClose)*100,2)
            firstReturnDict[str(year)] = diff1
                        
    
    second_df = df[df['Month']==monthDict[monthlyComparisonSecondMonth]]
    for year in second_df['Year'].unique():
        filtered_df = second_df[(second_df['TradingMonthDay'] >= secondPhenomenaDays[0]) 
                                & (second_df['Year']==year) 
                                & (second_df['TradingMonthDay'] <= secondPhenomenaDays[1])
                        ].reset_index(drop=True)
            
        if(len(filtered_df) > (secondPhenomenaDays[1]-secondPhenomenaDays[0])):
            firstClose = filtered_df.iloc[0]['Close']
            secondClose = filtered_df.iloc[-1]['Close']
            diff = round(secondClose - firstClose,2)
            diff1 = round((diff/firstClose)*100,2)
            secondReturnDict[str(year)] = diff1

    
    third_df = df[df['Month']==monthDict[monthlyComparisonThirdMonth]]
    for year in third_df['Year'].unique():
        filtered_df = third_df[(third_df['Year']==year)]
        if(len(filtered_df)>=abs(thirdPhenomenaDays[0])):   
            firstIndex =  filtered_df.index[thirdPhenomenaDays[0]]
            firstClose = filtered_df.loc[firstIndex,'Close']
            secondIndex = firstIndex + abs(thirdPhenomenaDays[0]) + thirdPhenomenaDays[1] -1           
            if(secondIndex <= len(original_df)):
                secondClose = original_df.loc[secondIndex]['Close']
                diff = round(secondClose - firstClose,2)
                diff1 = round((diff/firstClose)*100,2)
                thirdReturnDict[str(year)] = diff1
    
    #Return Figures and table
    global monthlyComparisonDatatableDownload
    global monthlyComparison_df
    monthlyComparison_dfPlot = monthlyComparison_df.to_dict('records')
    
    monthlyComparison_df['Year'] = yearsList
    monthlyComparison_df['Year'] = monthlyComparison_df['Year'].astype(str)
    firstReturnDf = pd.DataFrame(list(firstReturnDict.items()), columns=['Year',columnsToPlot1[0]])
    monthlyComparison_df = pd.merge(monthlyComparison_df, firstReturnDf, on='Year', how='left')
    secondReturnDf = pd.DataFrame(list(secondReturnDict.items()), columns=['Year', columnsToPlot1[1]])  
    monthlyComparison_df = pd.merge(monthlyComparison_df, secondReturnDf, on='Year', how='left')
    thirdReturnDf = pd.DataFrame(list(thirdReturnDict.items()), columns=['Year', columnsToPlot1[2]])        
    monthlyComparison_df = pd.merge(monthlyComparison_df, thirdReturnDf, on='Year', how='left')

    if (len(monthlyComparison_df) > 0):
        # print(monthlyComparison_df)
        allReturnColumns = monthlyComparison_df.columns.to_list()   
        for column in allReturnColumns:
            if(column==columnsToPlot1[0]):
                if(monthlyComparisonFirstReturnType==0):
                    monthlyComparison_df[column] = monthlyComparison_df[monthlyComparison_df[column]<0][column]
                elif(monthlyComparisonFirstReturnType==1):
                    monthlyComparison_df[column] = monthlyComparison_df[monthlyComparison_df[column]>0][column]
            if(column==columnsToPlot1[1]):
                if(monthlyComparisonSecondReturnType==0):
                    monthlyComparison_df[column] = monthlyComparison_df[monthlyComparison_df[column]<0][column]
                elif(monthlyComparisonSecondReturnType==1):                        
                    monthlyComparison_df[column] = monthlyComparison_df[monthlyComparison_df[column]>0][column]
            if(column==columnsToPlot1[2]):
                if(monthlyComparisonThirdReturnType==0):
                    monthlyComparison_df[column] = monthlyComparison_df[monthlyComparison_df[column]<0][column]
                elif(monthlyComparisonThirdReturnType==1):
                    monthlyComparison_df[column] = monthlyComparison_df[monthlyComparison_df[column]>0][column]
        monthlyComparison_df = monthlyComparison_df.dropna(how='any')
        
        if(len(monthlyComparison_df)>0):
            monthlyComparison_df = monthlyComparison_df[['Year']+columnsToPlot]
            allReturnColumns = monthlyComparison_df.columns
            totalCount = [monthlyComparison_df[colName].count() for colName in allReturnColumns[1:]]
            averageReturns = [round(i, 2) for i in monthlyComparison_df[allReturnColumns[1:]].mean()]
            totalSum = [round(i, 2) for i in monthlyComparison_df[allReturnColumns[1:]].sum()]
            positiveCount = [monthlyComparison_df[colName][monthlyComparison_df[colName] > 0].count() for colName in allReturnColumns[1:]]
            positiveMean = [round(monthlyComparison_df[colName][monthlyComparison_df[colName] > 0].mean(), 2) for colName in allReturnColumns[1:]]
            positiveSum = [round(monthlyComparison_df[colName][monthlyComparison_df[colName] > 0].sum(), 2) for colName in allReturnColumns[1:]]
            negativeCount = [monthlyComparison_df[colName][monthlyComparison_df[colName] < 0].count() for colName in allReturnColumns[1:]]
            negativeMean = [round(monthlyComparison_df[colName][monthlyComparison_df[colName] < 0].mean(), 2) for colName in allReturnColumns[1:]]
            negativeSum = [round(monthlyComparison_df[colName][monthlyComparison_df[colName] < 0].sum(), 2) for colName in allReturnColumns[1:]]
            
            monthlyComparison_df = pd.concat([monthlyComparison_df,  pd.DataFrame({value: [[*['All Count'], *totalCount][i]] for i, value in enumerate(allReturnColumns)})])
            monthlyComparison_df = pd.concat([monthlyComparison_df,  pd.DataFrame({value: [[*['Pos Count'], *positiveCount][i]] for i, value in enumerate(allReturnColumns)})])
            monthlyComparison_df = pd.concat([monthlyComparison_df,  pd.DataFrame({value: [[*['Neg Count'], *negativeCount][i]] for i, value in enumerate(allReturnColumns)})])
            monthlyComparison_df = pd.concat([monthlyComparison_df,  pd.DataFrame({value: [[*['Avg Return All'], *averageReturns][i]] for i, value in enumerate(allReturnColumns)})])
            monthlyComparison_df = pd.concat([monthlyComparison_df,  pd.DataFrame({value: [[*['Avg Return Pos'], *positiveMean][i]] for i, value in enumerate(allReturnColumns)})])
            monthlyComparison_df = pd.concat([monthlyComparison_df,  pd.DataFrame({value: [[*['Avg Return Neg'], *negativeMean][i]] for i, value in enumerate(allReturnColumns)})])
            monthlyComparison_df = pd.concat([monthlyComparison_df,  pd.DataFrame({value: [[*['Sum Return All'], *totalSum][i]] for i, value in enumerate(allReturnColumns)})])
            monthlyComparison_df = pd.concat([monthlyComparison_df,  pd.DataFrame({value: [[*['Sum Return Pos'], *positiveSum][i]] for i, value in enumerate(allReturnColumns)})])
            monthlyComparison_df = pd.concat([monthlyComparison_df,  pd.DataFrame({value: [[*['Sum Return Neg'], *negativeSum][i]] for i, value in enumerate(allReturnColumns)})])
            
            monthlyComparison_df = monthlyComparison_df.fillna(0)
            monthlyComparison_dfPlot = monthlyComparison_df.to_dict('records')
            monthlyComparison_df = monthlyComparison_df.set_index('Year')
                
    return monthlyComparison_dfPlot

@app.callback(
    Output(component_id='phenomena_monthtlyComparisonDataTable_download_csv', component_property='data'),
    Input('phenomena_monthlyComparisonDataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def allDayDataTable_download_daily(
    monthlyComparisonDataTable_download_button
):
    return monthlyComparisonDatatableDownload

if __name__ == '__main__':
    app.run_server(debug=True)