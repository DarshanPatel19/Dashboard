from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os
from itertools import zip_longest

from helper import symbolNamesToDropdown, specialDaysToDropdown, monthFullNames, weekDays, tradingDays, calenderDays, getDataTableForPlot, getDataTableStatistics, getMonthNumber, getHistoricTrendingDays


animatedChartsLayout = html.Div([

    html.Br(), html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Symbol'), width=5, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('Select Date Range'), width=5, align='left', style={'color': '#00218fa1'})
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='animatedCharts_symbolNameToPlot',
                                   options=symbolNamesToDropdown,
                                   value='BANKNIFTY',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=5, align='left'
        ),
        dbc.Col(
            dcc.DatePickerRange(id='animatedCharts_dataRange',
                                min_date_allowed=date(1800, 1, 1), max_date_allowed=date(2025, 12, 31),
                                start_date=date(2016, 1, 1), end_date=date(2023, 12, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=5, align='left'
        ),
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Weekday'), width=5, align='left', style={'color': '#00218fa1'}),
        dbc.Col(html.H6('Select Month'), width=5, align='left', style={'color': '#00218fa1'})
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='animatedCharts_selectedWeekdays',
                                   options=weekDays,
                                   value=weekDays, multi=True,
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=5, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Dropdown(id='animatedCharts_selectedMonths',
                                   options=monthFullNames,
                                   value=monthFullNames, multi=True,
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=5, align='left'
        ),
    ]),

    html.Br(), html.Br(),
    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='animatedCharts_allDayDataTable',
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
            width=11, align='left'
        )
    ]),

    html.Br(), html.Br(),
    dcc.Graph(id='animatedCharts_weekdaysToReturnsWithYearChange', style=dict(height='90vh')),



    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),

],
    style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)


@callback(
    [
        # Output(component_id='animatedCharts_allDayDataTable', component_property='data'),
        Output(component_id='animatedCharts_weekdaysToReturnsWithYearChange', component_property='figure')
    ],
    [
        Input('animatedCharts_symbolNameToPlot', 'value'), Input('animatedCharts_dataRange', 'start_date'), Input('animatedCharts_dataRange', 'end_date'),
        Input('animatedCharts_selectedWeekdays', 'value'), Input('animatedCharts_selectedMonths', 'value')
    ]
)
def display_animatedCharts(
    symbolNameToPlot, dataRangeStartDate, dataRangeEndDate,
    selectedWeekdays, selectedMonths
):
    df = pd.read_csv('./Symbols/' + symbolNameToPlot + '/1_Daily.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
    df = df.dropna()

    df = df[(df['Date'] >= dataRangeStartDate) & (df['Date'] <= dataRangeEndDate)]
    df = df[df['Weekday'].isin(selectedWeekdays)]
    df = df[df['Date'].dt.month.isin([getMonthNumber(selectedMonth) for selectedMonth in selectedMonths])]

    # Create a categorical data type with the custom order
    weekdayCategory = pd.Categorical(df['Weekday'], categories=weekDays, ordered=True)
    df['Weekday'] = weekdayCategory

    allDayDataTableReturnPlot = df[['Date', 'Open', 'High', 'Low', 'Close', 'Weekday', 'ReturnPercentage']] \
        .groupby([df['Date'].dt.year, 'Weekday'])['ReturnPercentage'].mean().round(2) \
        .reset_index().sort_values(by=['Date', 'Weekday'])

    # Chart of weekdays with returnChange with change of year interval
    weekdaysToReturnsWithYearChange = px.line(
        allDayDataTableReturnPlot, x='Weekday', y='ReturnPercentage',
        animation_frame='Date',
        range_y=[allDayDataTableReturnPlot['ReturnPercentage'].min()-0.1, allDayDataTableReturnPlot['ReturnPercentage'].max()+0.1]
    )
    weekdaysToReturnsWithYearChange.update_xaxes(
        categoryorder='array', categoryarray=weekDays,
        rangeslider_visible=False,
        showline=True, linewidth=1, linecolor='grey',
        gridcolor='grey', griddash='dot',
        showspikes=True, spikemode='across', spikesnap='cursor',
        spikecolor='grey', spikethickness=1, spikedash='dash',
        fixedrange=False
    )
    weekdaysToReturnsWithYearChange.update_yaxes(
        showline=True, linewidth=1, linecolor='grey',
        gridcolor='grey', griddash='dot',
        showspikes=True, spikemode='across', spikesnap='cursor',
        spikecolor='grey', spikethickness=1, spikedash='dash',
        fixedrange=False
    )
    weekdaysToReturnsWithYearChange.update_layout(
        yaxis_title='ReturnPercentage',
        title='Weekdays per Year',
        sliders=[dict(currentvalue={'prefix': 'Year: '})],
        hovermode='x unified', hoverdistance=100,
        font=dict(
            family='Courier New, blue',
            size=15,
            color='RebeccaPurple'
        ),
        updatemenus=[dict(buttons=[
            dict(args=[
                None, {'frame': {'duration': 1500,
                                 'redraw': False},
                       'fromcurrent': True,
                       'transition': {'duration': 1500, 'easing': 'quadratic-in-out'}}
            ], label='Play', method='animate'),
            dict(args=[
                [None], {'frame': {'duration': 0,
                                   'redraw': False},
                         'mode': 'immediate',
                         'transition': {'duration': 0}}
            ], label='Pause', method='animate')
        ])]
    )
    weekdaysToReturnsWithYearChange.add_hline(y=0, line_width=1, line_dash='dash', line_color='grey')

    """
        End of Code
    """

    return [
        # allDayDataTableReturnPlot.to_dict('records'),
        weekdaysToReturnsWithYearChange
    ]
