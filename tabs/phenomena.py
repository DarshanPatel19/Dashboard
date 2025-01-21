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


phenomenaDatatableDownload1 = pd.DataFrame()
phenomenaDatatableDownload2 = pd.DataFrame()



phenomenaLayout = html.Div([

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
    html.Hr(style={'border': '1px solid #00218fa1'}),


    html.H4('Phenomena Selection Filters', style={'color': '#00218fa1'}),
    html.Br(),
    
    dbc.Row([
        dbc.Col(html.H5('First Phenomenon'), width=6, align='left'),
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select Days'), width=8, align='left'),
    ]),
    dbc.Row([
       dbc.Col(
            html.Div([dcc.RangeSlider(
                        id='phenomena_selectionFirst',
                        min=1, max=23,
                        marks = {str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(1, 24, 1)},
                        dots=False, updatemode='drag', allowCross=False,
                        tooltip=dict(always_visible=True, placement='bottom'),
                        value=[2, 13],
                        persistence=True, persistence_type='session')],
                style=dict(width='90%')),
            width=8, align='left'
        ),
       
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select Month'), width=4, align='left'),
        dbc.Col(html.H6('Select Returns'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='phenomena_selectionFirstMonth',
                                   options = monthNames + ['Any'],
                                   value='Any',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
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
    html.Br(), html.Br(),

    dbc.Row([
        dbc.Col(html.H5('Second Phenomenon'), width=6, align='left'),
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select Days'), width=8, align='left'),
    ]),
    dbc.Row([
       dbc.Col(
            html.Div([dcc.RangeSlider(id='phenomena_selectionSecond',
                                      min=1, max=23,
                                      marks = {str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(1,24, 1)},
                                      dots=False, updatemode='drag', allowCross=False,
                                      tooltip=dict(always_visible=True, placement='bottom'),
                                      value=[13, 16],
                                      persistence=True, persistence_type='session')],
                     style=dict(width='90%')),
            width=8, align='left'
        ),
       
    ]),
   html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Select Month'), width=4, align='left'),
        dbc.Col(html.H6('Select Returns'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='phenomena_selectionSecondMonth',
                                    options = monthNames + ['Any'],
                                    value='Any',
                                    clearable=False, maxHeight=200,
                                    persistence=True, persistence_type='session'
                                    )],
                        style=dict(width='70%')),
            width=4, align='left'
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
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.RangeSlider(
                        id='phenomena_selectionThird',
                        min=-10, max=10,
                        marks = {str(h): {'label': str(h), 'style': {'color': 'black'}} for h in range(-10, 11, 1)},
                        dots=False, updatemode='drag', allowCross=False,
                        tooltip=dict(always_visible=True, placement='bottom'),
                        value=[-5, 2],
                        persistence=True, persistence_type='session')],
                        style=dict(width='90%')),
            width=8, align='left'
        ),
        
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select Month'), width=4, align='left'),
        dbc.Col(html.H6('Select Returns'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([dcc.Dropdown(id='phenomena_selectionThirdMonth',
                                   options = monthNames + ['Any'],
                                   value='Any',
                                   clearable=False, maxHeight=200,
                                   persistence=True, persistence_type='session'
                                   )],
                     style=dict(width='70%')),
            width=4, align='left'
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
    dbc.Button(id='phenomena_DataTable_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='phenomena_DataTable_download_csv'),
    dbc.Row([
        dbc.Col(
            html.Div(id='phenomena_DataTable', style=dict(width='100%')),
            width = 12, align='left'
        )
    ]),
    html.Br(),
    dcc.Graph(id='phenomena_filteredChart_1', style=dict(height='90vh')),
    html.Br(),
    dcc.Graph(id='phenomena_filteredChart_2', style=dict(height='90vh')),
    html.Br(), html.Br(),
    html.H4('Filtered Table'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Select the Phenomena to Display'), width=4, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='phenomena_datatable_selection_2',
                            inline=True,
                            options=[dict(label='First', value=1),
                                    dict(label='Second', value=2),
                                    dict(label='Third', value=3),],
                            value=1,
                            className='radiobutton-group',
                            persistence=True, persistence_type='session'),
            width=4, align='left'
        ),
    ]),
    dbc.Button(id='phenomena_DataTable_download_button2',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='phenomena_DataTable_download_csv2'),
    dbc.Row([
        dbc.Col(
            html.Div(id='phenomena_DataTable_2', style=dict(width='100%')),
            width = 6, align='left'
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

@callback(
    [
        Output(component_id='phenomena_DataTable', component_property='children'),
        Output(component_id='phenomena_DataTable_2', component_property='children'),
        Output(component_id='phenomena_filteredChart_1', component_property='figure'),
        Output(component_id='phenomena_filteredChart_2', component_property='figure'),
    ],
    [
        Input('phenomena_symbolNameToPlot', 'value'), 
        Input('phenomena_dateRange', 'start_date'), 
        Input('phenomena_dateRange', 'end_date'),
        Input('phenomena_positiveNegativeYears', 'value'), 
        Input('phenomena_evenOddYears', 'value'),
        Input('phenomena_selectionFirst', 'value'), 
        Input('phenomena_selectionFirstMonth', 'value'),
        Input('phenomena_selectionFirstReturns', 'value'), 
        Input('phenomena_selectionSecond', 'value'),
        Input('phenomena_selectionSecondMonth', 'value'),
        Input('phenomena_selectionSecondReturns', 'value'), 
        Input('phenomena_selectionThird', 'value'),
        Input('phenomena_selectionThirdMonth', 'value'),
        Input('phenomena_selectionThirdReturns', 'value'), 
        Input('phenomena_datatable_selection_2', 'value'),    
    ]
)
def display_phenomena(symbolNameToPlotValue, startDate, endDate, 
    positiveNegativeYearFilter, evenOddYearFilter,
    firstPhenomenaDays, firstPhenomenaMonth, firstPhenomenaReturnsFilter,
    secondPhenomenaDays, secondPhenomenaMonth, secondPhenomenaReturnsFilter,                          
    thirdPhenomenaDays, thirdPhenomenaMonth, thirdPhenomenaReturnsFilter,
    datatableFilter_2                          
):
    df = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/1_Daily.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
    df = df.dropna()
    original_df = df.copy(deep=True)
    df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)]
    
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
    
    #Get specific columns data to be used
    df = df[['Ticker', 'Date', 'Close', 'Month', 'Year', 'TradingMonthDay']]
    
    #Return Figures and table
    dfpheomenaChart_2 = pd.DataFrame()
    pheomenaChart_1 = go.Figure()
    pheomenaChart_2 = go.Figure()
    global phenomenaDatatableDownload1
    global phenomenaDatatableDownload2
    
    # Combined Table
    columnsToPlot = list()
    columnsToPlot = (
            [f'({days[0]},{days[1] - days[0]})' for days in [firstPhenomenaDays]] +
            [f'({days[0]},{days[1] - days[0]})' for days in [secondPhenomenaDays]] +
            [f'({abs(days[0])},{days[1]})' for days in [thirdPhenomenaDays]]           
        )
    columnsToPlot_2 = list()
    if(datatableFilter_2==1):
        columnsToPlot_2 = [f'({days[0]},{days[1] - days[0]})' for days in [firstPhenomenaDays]]
    elif(datatableFilter_2==2):
        columnsToPlot_2 = [f'({days[0]},{days[1] - days[0]})' for days in [secondPhenomenaDays]]
    else:
        columnsToPlot_2 = [f'({abs(days[0])},{days[1]})' for days in [thirdPhenomenaDays]]           
    

    diff = diff1 = None
    firstReturnDict = defaultdict(lambda: defaultdict(list))
    secondReturnDict = defaultdict(lambda: defaultdict(list))
    thirdReturnDict = defaultdict(lambda: defaultdict(list))
    
    yearsList = list(df['Year'].unique())
    monthDict = {'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
    monthDict1 = { 1:'Jan', 2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    
    first_df = df.copy(deep=True)
    second_df = df.copy(deep=True)
    third_df = df.copy(deep=True)

    if(firstPhenomenaMonth!="Any"):
        first_df = df[df['Month']==monthDict[firstPhenomenaMonth]]
    if(secondPhenomenaMonth!="Any"):
        second_df = df[df['Month']==monthDict[secondPhenomenaMonth]]
    if(thirdPhenomenaMonth!="Any"):
        third_df = df[df['Month']==monthDict[thirdPhenomenaMonth]]
    
    if(len(first_df)>0):
        for year in yearsList:
            for month in first_df['Month'].unique():
                filtered_df = pd.DataFrame()
                filtered_df = third_df[(third_df['TradingMonthDay'] >= thirdPhenomenaDays[0]) 
                                        & (third_df['Year']==year)
                                        & (first_df['Month']==month)
                                        & (third_df['TradingMonthDay'] <= thirdPhenomenaDays[1])
                            ].reset_index(drop=True)
                if(len(filtered_df)>0):
                    firstClose = filtered_df.iloc[0]['Close']
                    secondClose = filtered_df.iloc[-1]['Close']
                    diff = round(secondClose - firstClose,2)
                    diff1 = round((diff/firstClose)*100,2)
                    thirdReturnDict[monthDict1[month] + '-' +str(year)] = [diff, diff1]

    if(len(second_df)>0):
        for year in yearsList:
            for month in second_df['Month'].unique():
                filtered_df = pd.DataFrame()
                filtered_df = second_df[(second_df['TradingMonthDay'] >= secondPhenomenaDays[0]) 
                                        & (second_df['Year']==year) 
                                        & (second_df['Month']==month) 
                                        & (second_df['TradingMonthDay'] <= secondPhenomenaDays[1])
                            ].reset_index(drop=True)
                if(len(filtered_df)>0):
                    firstClose = filtered_df.iloc[0]['Close']
                    secondClose = filtered_df.iloc[-1]['Close']
                    diff = round(secondClose - firstClose,2)
                    diff1 = round((diff/firstClose)*100,2)
                    secondReturnDict[monthDict1[month] + '-' + str(year)] = [diff, diff1]

    if(len(third_df)>0):
        for year in yearsList:
            for month in third_df['Month'].unique():
                filtered_df = pd.DataFrame()
                filtered_df = first_df[(first_df['TradingMonthDay'] == firstPhenomenaDays[1]) 
                                        & (first_df['Year']==year)
                                        & (first_df['Month']==month)
                                        ]
                if(len(filtered_df)>0):
                    firstIndex = filtered_df.index[0]
                    if((firstIndex+firstPhenomenaDays[0]) >=0):
                        firstClose = original_df.loc[firstIndex - (abs(firstPhenomenaDays[0]) + firstPhenomenaDays[1] -1)]['Close']
                    else:
                        firstClose = 0
                    secondClose = filtered_df['Close'].values[0]
                    diff = round(secondClose - firstClose,2)
                    diff1 = round((diff/firstClose)*100,2)
                    firstReturnDict[monthDict1[month] + '-' +str(year)] = [diff, diff1]
  
    all_keys = set(firstReturnDict.keys()) | set(secondReturnDict.keys()) | set(thirdReturnDict.keys())
    sorted_all_keys = sorted(all_keys, key=lambda x: (x.split('-')[1], monthDict[x.split('-')[0]]), reverse=False)
    new_columns = pd.MultiIndex.from_product([columnsToPlot, ['ReturnPoints', 'ReturnPercentage']], names=['Phenomena', 'ReturnType'])
    data = []
    
    # Get Combined Data
    for key in sorted_all_keys:
        row_data = {}
        for phenomena in columnsToPlot:
            value1, value2 = None, None
            if phenomena == columnsToPlot[0] and key in firstReturnDict:
                value1, value2 = firstReturnDict[key]
            elif phenomena == columnsToPlot[1] and key in secondReturnDict:
                value1, value2 = secondReturnDict[key]
            elif key in thirdReturnDict:
                value1, value2 = thirdReturnDict[key]
            row_data['Date'] = key
            row_data[(phenomena, 'ReturnPoints')] = value1
            row_data[(phenomena, 'ReturnPercentage')] = value2
        data.append(row_data)
    
    final_df = final_df_2 = pd.DataFrame()
    df_columns = [' ']
    df_data = [np.NaN]
    df_columns_2 = [' ']
    df_data_2 = [np.NaN]

    # Create MultiIndex combined and Filtered Table
    if len(data) > 0:
        final_df = pd.DataFrame(data)
        final_df.set_index('Date', inplace=True) 
        final_df.columns = new_columns 
        final_df_2 = final_df.copy(deep=True)
        final_df = final_df.dropna(how='all').reset_index()
        allReturnColumns = final_df.columns 
        final_df['TotalPoints'] = final_df['TotalPercentage'] = 0
        for column in final_df.columns[1:]:
            if 'ReturnPoints' in column:
                final_df['TotalPoints'] = final_df['TotalPoints'] + final_df[column]
            if 'ReturnPercentage' in column:
                final_df['TotalPercentage'] =  final_df['TotalPercentage'] + final_df[column]
        final_df['TotalPoints'] = round(final_df['TotalPoints'], 2)
        final_df['TotalPercentage'] = round(final_df['TotalPercentage'], 2)
        
        
        for phenomena in columnsToPlot:
            final_df[('Percentage Contribution', phenomena)] = round((final_df[phenomena]['ReturnPoints']/abs(final_df['TotalPoints'])) * 100,2)
        
        totalCount = [final_df[colName].count() for colName in allReturnColumns[1:]]
        averageReturns = [round(i, 2) for i in final_df[allReturnColumns[1:]].mean()]
        totalSum = [round(i, 2) for i in final_df[allReturnColumns[1:]].sum()]
        positiveCount = [final_df[colName][final_df[colName] > 0].count() for colName in allReturnColumns[1:]]
        positiveMean = [round(final_df[colName][final_df[colName] > 0].mean(), 2) for colName in allReturnColumns[1:]]
        positiveSum = [round(final_df[colName][final_df[colName] > 0].sum(), 2) for colName in allReturnColumns[1:]]
        negativeCount = [final_df[colName][final_df[colName] < 0].count() for colName in allReturnColumns[1:]]
        negativeMean = [round(final_df[colName][final_df[colName] < 0].mean(), 2) for colName in allReturnColumns[1:]]
        negativeSum = [round(final_df[colName][final_df[colName] < 0].sum(), 2) for colName in allReturnColumns[1:]]
        
        final_df = pd.concat([final_df,  pd.DataFrame({value: [[*['All Count'], *totalCount][i]] for i, value in enumerate(allReturnColumns)})])
        final_df = pd.concat([final_df,  pd.DataFrame({value: [[*['Positive Count'], *positiveCount][i]] for i, value in enumerate(allReturnColumns)})])
        final_df = pd.concat([final_df,  pd.DataFrame({value: [[*['Negative Count'], *negativeCount][i]] for i, value in enumerate(allReturnColumns)})])
        final_df = pd.concat([final_df,  pd.DataFrame({value: [[*['Average Return of All'], *averageReturns][i]] for i, value in enumerate(allReturnColumns)})])
        final_df = pd.concat([final_df,  pd.DataFrame({value: [[*['Average Return of Positive'], *positiveMean][i]] for i, value in enumerate(allReturnColumns)})])
        final_df = pd.concat([final_df,  pd.DataFrame({value: [[*['Average Return of Negative'], *negativeMean][i]] for i, value in enumerate(allReturnColumns)})])
        final_df = pd.concat([final_df,  pd.DataFrame({value: [[*['Sum Return of All'], *totalSum][i]] for i, value in enumerate(allReturnColumns)})])
        final_df = pd.concat([final_df,  pd.DataFrame({value: [[*['Sum Return of Positive'], *positiveSum][i]] for i, value in enumerate(allReturnColumns)})])
        final_df = pd.concat([final_df,  pd.DataFrame({value: [[*['Sum Return of Negative'], *negativeSum][i]] for i, value in enumerate(allReturnColumns)})])
        phenomenaDatatableDownload1 = dcc.send_data_frame(final_df.set_index('Date').to_csv, 'Youngturtle_PhenomenaReturns.csv')

        df_columns, df_data = datatable_settings_multiindex(final_df) 
       
        dfpheomenaChart_2['ReturnPercentage'] = averageReturns[0:5:2]
        dfpheomenaChart_2['Phenomena'] = columnsToPlot

        for index, row in dfpheomenaChart_2.iterrows():
            pheomenaChart_1.add_trace(go.Scatter(
                x=[row['Phenomena']], 
                y=[row['ReturnPercentage']],  
                mode='markers', 
                name=str(row['ReturnPercentage']), 
                text=[row['Phenomena'] + ': ' + str(row['ReturnPercentage'])], 
                hoverinfo='text ',  
            ))
            pheomenaChart_1.add_trace(go.Scatter(
                x=[row['Phenomena'], dfpheomenaChart_2.loc[0]['Phenomena']], 
                y=[row['ReturnPercentage'], 0],  
                mode='lines+markers',
                showlegend=False, 
                hoverinfo = 'skip',
            ))
       
        pheomenaChart_1.update_layout(
            title='Phenomena Average Returns',
            xaxis_title='Phenomena',
            yaxis_title='Average Return Percentage',
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
        
        pheomenaChart_2 = go.Figure(data=[go.Bar(x=dfpheomenaChart_2['Phenomena'], y=dfpheomenaChart_2['ReturnPercentage'])])
        pheomenaChart_2.update_layout(
            title ='Phenomena Average Returns',
            xaxis_title='Phenomena',
            yaxis_title='Average Return Percentage',
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

    if(len(final_df_2)>0):
        for column in columnsToPlot:
            if(column==columnsToPlot[0]):
                if(firstPhenomenaReturnsFilter==1):
                    final_df_2[(column,'ReturnPoints')] = final_df_2[final_df_2[(column,'ReturnPoints')]>0][(column, 'ReturnPoints')]
                    final_df_2[(column,'ReturnPercentage')] = final_df_2[final_df_2[(column,'ReturnPercentage')]>0][(column, 'ReturnPercentage')]
                elif(firstPhenomenaReturnsFilter==2):
                    final_df_2[(column,'ReturnPoints')] = final_df_2[final_df_2[(column,'ReturnPoints')]<0][(column, 'ReturnPoints')]
                    final_df_2[(column,'ReturnPercentage')] = final_df_2[final_df_2[(column,'ReturnPercentage')]<0][(column, 'ReturnPercentage')]
            elif(column==columnsToPlot[1]):
                if(secondPhenomenaReturnsFilter==1):
                    final_df_2[(column,'ReturnPoints')] = final_df_2[final_df_2[(column,'ReturnPoints')]>0][(column, 'ReturnPoints')]
                    final_df_2[(column,'ReturnPercentage')] = final_df_2[final_df_2[(column,'ReturnPercentage')]>0][(column, 'ReturnPercentage')]
                elif(secondPhenomenaReturnsFilter==2):
                    final_df_2[(column,'ReturnPoints')] = final_df_2[final_df_2[(column,'ReturnPoints')]<0][(column, 'ReturnPoints')]
                    final_df_2[(column,'ReturnPercentage')] = final_df_2[final_df_2[(column,'ReturnPercentage')]<0][(column, 'ReturnPercentage')]
            elif(column==columnsToPlot[2]):
                if(thirdPhenomenaReturnsFilter==1):
                    final_df_2[(column,'ReturnPoints')] = final_df_2[final_df_2[(column,'ReturnPoints')]>0][(column, 'ReturnPoints')]
                    final_df_2[(column,'ReturnPercentage')] = final_df_2[final_df_2[(column,'ReturnPercentage')]>0][(column, 'ReturnPercentage')]
                elif(thirdPhenomenaReturnsFilter==2):
                    final_df_2[(column,'ReturnPoints')] = final_df_2[final_df_2[(column,'ReturnPoints')]<0][(column, 'ReturnPoints')]
                    final_df_2[(column,'ReturnPercentage')] = final_df_2[final_df_2[(column,'ReturnPercentage')]<0][(column, 'ReturnPercentage')]         
        
        final_df_2 = final_df_2.dropna(how='any')    
        final_df_2 = final_df_2[columnsToPlot_2].reset_index()
           
        allReturnColumns = final_df_2.columns
        totalCount = [final_df_2[colName].count() for colName in allReturnColumns[1:]]
        averageReturns = [round(i, 2) for i in final_df_2[allReturnColumns[1:]].mean()]
        totalSum = [round(i, 2) for i in final_df_2[allReturnColumns[1:]].sum()]
        positiveCount = [final_df_2[colName][final_df_2[colName] > 0].count() for colName in allReturnColumns[1:]]
        positiveMean = [round(final_df_2[colName][final_df_2[colName] > 0].mean(), 2) for colName in allReturnColumns[1:]]
        positiveSum = [round(final_df_2[colName][final_df_2[colName] > 0].sum(), 2) for colName in allReturnColumns[1:]]
        negativeCount = [final_df_2[colName][final_df_2[colName] < 0].count() for colName in allReturnColumns[1:]]
        negativeMean = [round(final_df_2[colName][final_df_2[colName] < 0].mean(), 2) for colName in allReturnColumns[1:]]
        negativeSum = [round(final_df_2[colName][final_df_2[colName] < 0].sum(), 2) for colName in allReturnColumns[1:]]
        
        final_df_2 = pd.concat([final_df_2,  pd.DataFrame({value: [[*['All Count'], *totalCount][i]] for i, value in enumerate(allReturnColumns)})])
        final_df_2 = pd.concat([final_df_2,  pd.DataFrame({value: [[*['Positive Count'], *positiveCount][i]] for i, value in enumerate(allReturnColumns)})])
        final_df_2 = pd.concat([final_df_2,  pd.DataFrame({value: [[*['Negative Count'], *negativeCount][i]] for i, value in enumerate(allReturnColumns)})])
        final_df_2 = pd.concat([final_df_2,  pd.DataFrame({value: [[*['Average Return of All'], *averageReturns][i]] for i, value in enumerate(allReturnColumns)})])
        final_df_2 = pd.concat([final_df_2,  pd.DataFrame({value: [[*['Average Return of Positive'], *positiveMean][i]] for i, value in enumerate(allReturnColumns)})])
        final_df_2 = pd.concat([final_df_2,  pd.DataFrame({value: [[*['Average Return of Negative'], *negativeMean][i]] for i, value in enumerate(allReturnColumns)})])
        final_df_2 = pd.concat([final_df_2,  pd.DataFrame({value: [[*['Sum Return of All'], *totalSum][i]] for i, value in enumerate(allReturnColumns)})])
        final_df_2 = pd.concat([final_df_2,  pd.DataFrame({value: [[*['Sum Return of Positive'], *positiveSum][i]] for i, value in enumerate(allReturnColumns)})])
        final_df_2 = pd.concat([final_df_2,  pd.DataFrame({value: [[*['Sum Return of Negative'], *negativeSum][i]] for i, value in enumerate(allReturnColumns)})])
        final_df_2 = final_df_2.fillna(0)
        phenomenaDatatableDownload2 = dcc.send_data_frame(final_df_2.set_index('Date').to_csv, 'Youngturtle_PhenomenaFilteredReturns.csv')
        df_columns_2, df_data_2 = datatable_settings_multiindex(final_df_2)   
    

    return [dash_table.DataTable(
                id = 'phenomena_DataTable',
                columns = df_columns,
                data = df_data,
                merge_duplicate_headers =True,
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
                ]+[
                    {
                    'if': {
                            'column_id': col['id']
                    },
                    'textAlign': 'center',
                    'borderLeft': '2px solid black' ,
                    'borderRight': '2px solid black',
                    } for col in df_columns
                ],
                style_header_conditional=[
                    {
                    'if': {'column_id': col['id']},
                    'textAlign': 'center',
                    'borderLeft': '2px solid black',    
                    'borderRight': '2px solid black',
                } for col in df_columns],
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
    ),
    dash_table.DataTable(
        id = 'phenomena_DataTable_2',
        columns = df_columns_2,
        data = df_data_2,
        merge_duplicate_headers =True,
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
                ]+[
                    {
                    'if': {
                            'column_id': col['id']
                    },
                    'textAlign': 'center',
                    'borderLeft': '2px solid black',
                    'borderRight': '2px solid black',
                    } for col in df_columns_2
                ],
        style_header_conditional=[
                    {
                    'if': {'column_id': col['id']},
                    'textAlign': 'center',
                    'borderLeft': '2px solid black',
                    'borderRight': '2px solid black',
                } for col in df_columns_2],
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
    ),
    pheomenaChart_1,
    pheomenaChart_2,
    ]
    
@callback(
    Output(component_id='phenomena_DataTable_download_csv', component_property='data'),
    Input('phenomena_DataTable_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def allDayDataTable_download_daily(
    phenomena_DataTable_download_button
):
    return phenomenaDatatableDownload1

@callback(
    Output(component_id='phenomena_DataTable_download_csv2', component_property='data'),
    Input('phenomena_DataTable_download_button2', 'n_clicks'),
    prevent_initial_call=True
)
def allDayDataTable_download_daily(
    phenomena_DataTable_download_button2
):
    return phenomenaDatatableDownload2
