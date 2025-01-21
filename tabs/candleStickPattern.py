from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta
import os
from dateutil.relativedelta import relativedelta 
from time import time
# import pandas_ta as ta

assets_path = os.getcwd() + '/assets'

# app = Dash(__name__,
#         title='Seasonality',
#         assets_folder=assets_path, include_assets_files=True,
#         suppress_callback_exceptions=True,
#         external_stylesheets=[dbc.themes.LITERA],
#         meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
#         )

candleStickpatternLayout = html.Div([
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Candle Stick Pattern Input'),

    html.Br(),
    
    dbc.Row([
        dbc.Col(html.H6('Select Reference Date'), width=3, align='left'),
        dbc.Col(html.H6('Wick/Body Ratio'), width=3, align='left'),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.DatePickerRange(id='candleStickPattern_dataRange',
                                min_date_allowed=date(1900, 1, 1), max_date_allowed=date(2030, 12, 31),
                                start_date=date(2022, 1, 1), end_date=date(2022, 12, 31),
                                display_format='DD-MM-YYYY', month_format='DD-MM-YYYY',
                                stay_open_on_select=True, reopen_calendar_on_clear=True, show_outside_days=True,
                                persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='candleStickPattern_wickBodyRatio',
                                type='number', value= 2,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '90%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
    ]),
    html.Br(),
    
    dbc.Row([
        dbc.Col(html.H6('Bullish Engulfing'), width=3, align='left'),
        dbc.Col(html.H6('Bearish Engulfing'), width=3, align='left'),
        dbc.Col(html.H6('Hammer'), width=3, align='left'),
        dbc.Col(html.H6('Inverted Hammer'), width=3, align='left'),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='candleStickPattern_bullishEngulfing',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='candleStickPattern_bearishEngulfing',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='candleStickPattern_hammer',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='candleStickPattern_invertedHammer',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
    ]),
    
    html.Br(),
    dbc.Row([
        dbc.Col(html.H6('Bullish Piercing'), width=3, align='left'),
        dbc.Col(html.H6('Bearish Piercing'), width=3, align='left'),
        dbc.Col(html.H6('Morning Star'), width=3, align='left'),
        dbc.Col(html.H6('Evening Star'), width=3, align='left'),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='candleStickPattern_bullishPiercing',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='candleStickPattern_bearishPiercing',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='candleStickPattern_morningStar',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='candleStickPattern_eveningStar',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
    ]),
    
    html.Br(),
    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Bollinger Band Input'),

    html.Br(),
    
    dbc.Row([
        dbc.Col(html.H6('BB Toggle'), width=3, align='left'),
        dbc.Col(html.H6('BB Range'), width=3, align='left'),
        dbc.Col(html.H6('BB Width'), width=3, align='left'),
        dbc.Col(html.H6('Close Cross BB Top/Bottom'), width=3, align='left'),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='bollingerBond_Toggle',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='bollingerBond_Range',
                                type='number', value= 12,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
        dbc.Col(
            html.Div([dcc.Input(id='bollingerBond_Width',
                                type='number', value= 2,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
        dbc.Col(
            dcc.RadioItems(id='bollingerBond_CrossType',
                           inline=True,
                           options=[dict(label='Top', value=0),
                                    dict(label='Bottom', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
                           width=3, align='left'
        ),
    ]),
    
    html.Br(),
    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Relative Strength Index Input'),

    html.Br(),
    
    dbc.Row([
        dbc.Col(html.H6('RSI Toggle'), width=3, align='left'),
        dbc.Col(html.H6('RSI Period'), width=3, align='left'),
        dbc.Col(html.H6('RSI Threshold'), width=3, align='left'),
        dbc.Col(html.H6('RSI Cross Threshold Top/Bottom'), width=3, align='left'),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='relativeStrengthIndex_Toggle',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='relativeStrengthIndex_Period',
                                type='number', value= 14,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
        dbc.Col(
            html.Div([dcc.Input(id='relativeStrengthIndex_Threshold',
                                type='number', value= 2,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
        dbc.Col(
            dcc.RadioItems(id='relativeStrengthIndex_CrossType',
                           inline=True,
                           options=[dict(label='Top', value=0),
                                    dict(label='Bottom', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
                           width=3, align='left'
        ),
    ]),

    html.Br(),
    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('SuperTrend Long Loss Input'),

    html.Br(),
    
    dbc.Row([
        dbc.Col(html.H6('Long Loss Toggle'), width=3, align='left'),
        dbc.Col(html.H6('ST Period'), width=3, align='left'),
        dbc.Col(html.H6('ST Factor'), width=3, align='left'),
        dbc.Col(html.H6('Long Loss Type'), width=3, align='left'),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='supertrendLongLoss_Toggle',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='supertrendLongLoss_Period',
                                type='number', value= 14,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
        dbc.Col(
            html.Div([dcc.Input(id='supertrendLongLoss_Factor',
                                type='number', value= 2,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
        dbc.Col(
            dcc.RadioItems(id='supertrendLongLoss_LongLossType',
                           inline=True,
                           options=[dict(label='N Losses', value='N Losses'),
                                    dict(label='x% DrawDown', value='x% DrawDown'),],
                           value='N Losses',
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),

    ]),

    html.Br(),
    
    dbc.Row([
        dbc.Col(html.H6('Consecutive Toggle'), width=3, align='left'),
        dbc.Col(html.H6('Number Of Losses'), width=3, align='left'),
        dbc.Col(html.H6('Look Back Trades'), width=3, align='left'),
    ]),
    

    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='supertrendLongLoss_Consecutive',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
                           width=3, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='supertrendLongLoss_numOfLosses',
                                type='number', value= 2,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
        dbc.Col(
            html.Div([dcc.Input(id='supertrendLongLoss_lookBackPeriod',
                                type='number', value= 2,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
    ]),

    html.Br(),
    
    dbc.Row([
        dbc.Col(html.H6('x% DrawDown'), width=3, align='left'),
        dbc.Col(html.H6('Number Of Days'), width=3, align='left'),
        # dbc.Col(html.H6('Days Type'), width=3, align='left'),
    ]),

    dbc.Row([
        dbc.Col(
            html.Div([dcc.Input(id='supertrendLongLoss_xPercentDrawdown',
                                type='number', value= 2,
                                placeholder='Enter a Number(%)',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
        dbc.Col(
            html.Div([dcc.Input(id='supertrendLongLoss_numOfDaysDrawdown',
                                type='number', value= 2,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
        # dbc.Col(
        #     dcc.RadioItems(id='supertrendLongLoss_dayTypeDrawdown',
        #                    inline=True,
        #                    options=[dict(label='Calender Days', value='Calender Days'),
        #                             dict(label='Trading Days', value='Trading Days'),],
        #                    value='Calender Days',
        #                    className='radiobutton-group',
        #                    persistence=True, persistence_type='session'),
        #     width=3, align='left'
        # ),
    ]),
    
    html.Br(),
    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Lower High / Lower Low Input'),

    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('Lower High Toggle'), width=3, align='left'),
        dbc.Col(html.H6('Number of Lower Highs'), width=3, align='left'),
        dbc.Col(html.H6('Lower Lows= Toggle'), width=3, align='left'),
        dbc.Col(html.H6('Number of Lower Lows'), width=3, align='left'),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='lowerHighLows_LowerHighToggle',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='lowerHighLows_LowerHighDays',
                                type='number', value= 14,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
        dbc.Col(
            dcc.RadioItems(id='lowerHighLows_LowerLowToggle',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='lowerHighLows_LowerLowDays',
                                type='number', value= 14,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col(html.H6('AND/OR'), width=3, align='left'),
        dbc.Col(html.H6('Consecutive Toggle'), width=3, align='left'),
        dbc.Col(html.H6('LookBack Days'), width=3, align='left'),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='lowerHighLows_AndOrToggle',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=1,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            dcc.RadioItems(id='lowerHighLows_ConsecutiveToggle',
                           inline=True,
                           options=[dict(label='Off', value=0),
                                    dict(label='On', value=1),],
                           value=0,
                           className='radiobutton-group',
                           persistence=True, persistence_type='session'),
            width=3, align='left'
        ),
        dbc.Col(
            html.Div([dcc.Input(id='lowerHighLows_LookBackDays',
                                type='number', value= 14,
                                placeholder='Enter a Number',
                                style={'width': '90px', 'height': '30px'},
                                min=0, step=1,
                                persistence=True, persistence_type='session')],
                     style={'width': '70%', 'padding-top': '0px'}),
                        align='left',width=3,
        ),
    ]),

    html.Br(),
    html.Hr(style={'border': '1px solid #00218fa1'}),
    html.H2('Scanner Output'),
    html.Br(),
    
    dbc.Button(id='scanner_download_button',
               children=[html.I(className='fa fa-download'), 'Download'],
               color='primary',
               className='me-1'
               ),
    dcc.Download(id='scanner_download_csv'),

    dbc.Row([
        dbc.Col(
            html.Div([dash_table.DataTable(id='candleStickPattern_outputTable',                                      
                                           merge_duplicate_headers=True,
                                           editable=True,
                                           sort_action='native', sort_mode='multi',
                                           style_data_conditional=[
                                            {
                                                'if': {'column_id': colname},
                                                'border-right': '3px solid black'
                                            } for colname in ['ROC_1','ROC_2','ROC_3','ROC_4','ROC_5','Avg Rank']
                                           ],
                                           style_cell=dict(
                                               whiteSpace='pre-line'
                                           ),
                                           style_header=dict(
                                               width='8px', minWidth='8px', maxWidth='8px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='lightgrey', color='black', fontWeight='bold'
                                                ,textAlign='center'
                                           ),
                                           
                                           style_data=dict(
                                               width='8px', minWidth='8px', maxWidth='8px',
                                               overflow='hidden', textOverflow='ellipsis',
                                               backgroundColor='white', color='black',textAlign='center'
                                           )),],
                    style=dict(overflowX='auto', width='100%')),
            width=12, align='center'
        ),    
    ]),

    html.Br(),
    html.Br(),
    html.Br(),

],
 style={'padding-left': '50px', 'width': '99%', 'zoom': '100%'}
)


@callback(
        Output(component_id='candleStickPattern_outputTable', component_property='data'),
    [
        Input('candleStickPattern_dataRange', 'start_date'), Input('candleStickPattern_dataRange', 'end_date'),Input('candleStickPattern_wickBodyRatio','value'),
        Input('candleStickPattern_bullishEngulfing','value'),Input('candleStickPattern_bearishEngulfing','value'),Input('candleStickPattern_hammer','value'),Input('candleStickPattern_invertedHammer','value'),
        Input('candleStickPattern_bullishPiercing','value'),Input('candleStickPattern_bearishPiercing','value'),Input('candleStickPattern_morningStar','value'),Input('candleStickPattern_eveningStar','value'),
        Input('bollingerBond_Toggle','value') ,Input('bollingerBond_Range','value'),Input('bollingerBond_Width','value'),Input('bollingerBond_CrossType','value'),
        Input('relativeStrengthIndex_Toggle','value') ,Input('relativeStrengthIndex_Period','value') ,Input('relativeStrengthIndex_Threshold','value') ,Input('relativeStrengthIndex_CrossType','value') ,
        Input('supertrendLongLoss_Toggle','value') ,Input('supertrendLongLoss_Period','value') ,Input('supertrendLongLoss_Factor','value') ,Input('supertrendLongLoss_LongLossType','value'),
        Input('supertrendLongLoss_Consecutive','value') ,Input('supertrendLongLoss_numOfLosses','value'), Input('supertrendLongLoss_lookBackPeriod','value'),
        Input('supertrendLongLoss_xPercentDrawdown','value'), Input('supertrendLongLoss_numOfDaysDrawdown','value'),
        Input('lowerHighLows_LowerHighToggle','value'),Input('lowerHighLows_LowerHighDays','value'),Input('lowerHighLows_LowerLowToggle','value'),Input('lowerHighLows_LowerLowDays','value'),
        Input('lowerHighLows_AndOrToggle','value'),Input('lowerHighLows_ConsecutiveToggle','value'),Input('lowerHighLows_LookBackDays','value'),
    ]
)

def generate_performance_table(startDate, endDate,candleStickPattern_wickBodyRatio,
                               candleStickPattern_bullishEngulfingToggle,candleStickPattern_bearishEngulfingToggle, candleStickPattern_hammerToggle,candleStickPattern_invertedHammerToggle,
                               candleStickPattern_bullishPiercing,candleStickPattern_bearishPiercing, candleStickPattern_morningStar,candleStickPattern_eveningStar,
                               bollingerBond_Toggle,bollingerBond_Range,bollingerBond_Width,bollingerBond_CrossType,
                               relativeStrengthIndex_Toggle,relativeStrengthIndex_Period,relativeStrengthIndex_Threshold,relativeStrengthIndex_CrossType ,
                               supertrendLongLoss_Toggle,supertrendLongLoss_Period,supertrendLongLoss_Factor,supertrendLongLoss_LongLossType,
                               supertrendLongLoss_Consecutive,supertrendLongLoss_numOfLosses,supertrendLongLoss_lookBackPeriod,
                               supertrendLongLoss_xPercentDrawdown, supertrendLongLoss_numOfDaysDrawdown,
                               lowerHighLows_LowerHighToggle,lowerHighLows_LowerHighDays, lowerHighLows_LowerLowToggle,lowerHighLows_LowerLowDays,
                               lowerHighLows_AndOrToggle, lowerHighLows_ConsecutiveToggle, lowerHighLows_LookBackDays,
        ):
   
    tickerList = pd.read_csv('./Basket Stocks/Basket.csv')['Stocks'].tolist()
    candleStickPatternFinalDf = pd.DataFrame()
    global csvFinalDf
    csvFinalDf = pd.DataFrame()

    
    startTime = time()
    if startDate == None or endDate == None:
        return None
    
    # for ticker in tickerList:
    for ticker in tickerList:
        df = pd.read_csv(f'.//Symbols//{ticker}//1_Daily.csv')[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close']]
        
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df[df['Date'] <= endDate]

        if len(df) > 0:
            # Shift columns based on pattern toggles
            if any([candleStickPattern_bullishEngulfingToggle, candleStickPattern_bearishEngulfingToggle,
                    candleStickPattern_bullishPiercing, candleStickPattern_bearishPiercing,
                    candleStickPattern_morningStar, candleStickPattern_eveningStar,bollingerBond_Toggle]):
                df[['PPrevious_Open', 'PPrevious_High', 'PPrevious_Low', 'PPrevious_Close']] = df[['Open', 'High', 'Low', 'Close']].shift(2)
                df[['Previous_Open', 'Previous_High', 'Previous_Low', 'Previous_Close']] = df[['Open', 'High', 'Low', 'Close']].shift(1)
        
            # Filter and combine enabled patterns
            pattern_columns = []
            if candleStickPattern_bullishEngulfingToggle: 
                pattern_columns.append('Bullish_Engulfing')
                df['Bullish_Engulfing'] = (
                    candleStickPattern_bullishEngulfingToggle and
                    (df['Previous_Close'] < df['Previous_Open']) & (df['Close'] > df['Open']) &
                    (df['Open'] < df['Previous_Low']) & (df['Close'] > df['Previous_High'])
                )
            
            if candleStickPattern_bearishEngulfingToggle: 
                pattern_columns.append('Bearish_Engulfing')
                df['Bearish_Engulfing'] = (
                    candleStickPattern_bearishEngulfingToggle and
                    (df['Previous_Close'] > df['Previous_Open']) & (df['Close'] < df['Open']) &
                    (df['Open'] > df['Previous_High']) & (df['Close'] < df['Previous_Low'])
                )

            if candleStickPattern_hammerToggle: 
                pattern_columns.append('Hammer')
                df['Hammer'] = (
                    candleStickPattern_hammerToggle and
                    (df['Close'] != df['Open']) &
                    ((df[['Open', 'Close']].min(axis=1) - df['Low']) >= candleStickPattern_wickBodyRatio * abs(df['Close'] - df['Open'])) &
                    ((df['High'] - df[['Open','Close']].max(axis=1)) <= (0.15*(df[['Open','Close']].min(axis=1)-df['Low'])) )
                )
                
            if candleStickPattern_invertedHammerToggle: 
                pattern_columns.append('Inverted_Hammer')
                df['Inverted_Hammer'] = (
                    candleStickPattern_invertedHammerToggle and
                    (df['Close'] != df['Open']) &
                    ((df['High'] - df[['Open', 'Close']].max(axis=1)) > candleStickPattern_wickBodyRatio * abs(df['Close'] - df['Open'])) &
                    ((0.15*(df['High'] - df[['Open','Close']].max(axis=1))) >= (df[['Open','Close']].min(axis=1)-df['Low']) )
                )

            if candleStickPattern_bullishPiercing: 
                pattern_columns.append('Bullish_Piercing')
                df['Bullish_Piercing'] = (
                   candleStickPattern_bullishPiercing and
                    (df['Previous_Close'] < df['Previous_Open']) & (df['Open'] < df['Previous_Low']) &
                    (df['Close'] > (df['Previous_High'] + df['Previous_Low']) / 2)
                )
            if candleStickPattern_bearishPiercing: 
                pattern_columns.append('Bearish_Piercing')
                df['Bearish_Piercing'] = (
                    candleStickPattern_bearishPiercing and
                    (df['Previous_Close'] > df['Previous_Open']) & (df['Open'] > df['Previous_High']) &
                    (df['Close'] < (df['Previous_High'] + df['Previous_Low']) / 2)
                )

            if candleStickPattern_morningStar: 
                pattern_columns.append('Morning_Star')
                df['Morning_Star'] = (
                    candleStickPattern_morningStar and
                    (df['PPrevious_Close'] < df['PPrevious_Open']) &
                    (df['Previous_Open'] < df['PPrevious_Low']) &
                    (df['Previous_Close'] < df['PPrevious_Close']) &
                    (df['Open'] < df['Close']) &
                    (df['Close'] > (df['PPrevious_Close'] + df['PPrevious_Open']) / 2)
                )

            if candleStickPattern_eveningStar: 
                pattern_columns.append('Evening_Star')
                df['Evening_Star'] = (
                    candleStickPattern_eveningStar and
                    (df['PPrevious_Close'] > df['PPrevious_Open']) &
                    (df['Previous_Open'] > df['PPrevious_High']) &
                    (df['Previous_Close'] > df['PPrevious_Close']) &
                    (df['Open'] > df['Close']) &
                    (df['Close'] < (df['PPrevious_Close'] + df['PPrevious_Open']) / 2)
                )

            if bollingerBond_Toggle:
                bollingerBondColumnName = 'BB Below Lower Band' if bollingerBond_CrossType else 'BB Above Upper Band'
                
                pattern_columns.append(bollingerBondColumnName)
                bollingerBands = pd.DataFrame(ta.bbands(df['Close'], length=bollingerBond_Range, std=bollingerBond_Width))
                bollingerBands.columns = ['BB Lower Band', 'BB Middle Band', 'BB Upper Band', 'BB Bandwidth', 'BB %B']
                df = pd.concat([df, bollingerBands], axis=1)
                df[bollingerBondColumnName] = ((df['Close'] < df['BB Lower Band']) & (df['Previous_Close'] > df['BB Lower Band'])) \
                                        if bollingerBond_CrossType \
                                        else ((df['Close'] > df['BB Upper Band']) & (df['Previous_Close'] < df['BB Upper Band']))

            if relativeStrengthIndex_Toggle:
                relativeStrengthIndexColumnName = 'RSI Below Threshold' if relativeStrengthIndex_CrossType else 'RSI Above Threshold'
                pattern_columns.append(relativeStrengthIndexColumnName)
                df['RSI'] = ta.rsi(df['Close'], length=relativeStrengthIndex_Period)
                df['Previous RSI'] = df['RSI'].shift(1)
                df[relativeStrengthIndexColumnName] = ((df['RSI'] < relativeStrengthIndex_Threshold) & (df['Previous RSI'] > relativeStrengthIndex_Threshold))  \
                                                    if relativeStrengthIndex_CrossType  \
                                                    else ((df['RSI'] > relativeStrengthIndex_Threshold) & (df['Previous RSI'] < relativeStrengthIndex_Threshold))

            if supertrendLongLoss_Toggle:
                pattern_columns.append('Long Loss Entry')
                sti = pd.DataFrame(ta.supertrend(df['High'], df['Low'], df['Close'], length=supertrendLongLoss_Period, multiplier=supertrendLongLoss_Factor))
                
                sti.columns = ['ST Value','ST Sig','ST Bull Value','ST Bear Value']
                
                longLossDf = pd.concat([df, sti], axis=1).copy()

                longLossDf = longLossDf[(longLossDf['ST Sig'] != longLossDf['ST Sig'].shift(1))]
                longLossDf['ST P/L'] = ((longLossDf['Close']/longLossDf['Close'].shift(1))-1)*100


                if supertrendLongLoss_LongLossType == 'N Losses':
                    longLossDf['Long Loss'] = (longLossDf['ST Sig'] == -1) & (longLossDf['ST P/L'] < 0)
                    longLossDf['Long Loss Entry'] = (longLossDf['Long Loss'].rolling(window=(supertrendLongLoss_lookBackPeriod if supertrendLongLoss_Consecutive else supertrendLongLoss_numOfLosses)*2).\
                                                            sum().shift(1).fillna(0).astype(int) >= supertrendLongLoss_numOfLosses) & (longLossDf['ST Sig'] == 1)
                    df['Long Loss Entry'] = df['Date'].map(longLossDf.set_index('Date')['Long Loss Entry']).fillna(False).astype(bool)
                else:
                    
                    OriginalLongLossDf = longLossDf.copy()
                    longLossDf = longLossDf[longLossDf['ST Sig'] == -1].reset_index(drop=True)
                    longLossDf['Long Loss Entry'] = False
                    
                    for k in range(len(longLossDf)):
                        current_date = longLossDf.loc[k, 'Date']

                        mask = (longLossDf['Date'] <= current_date) & (longLossDf['Date'] >= (current_date - pd.Timedelta(days=supertrendLongLoss_numOfDaysDrawdown))) # type: ignore
                        previous_rows = longLossDf[mask]
                        
                        if len(previous_rows) > 0:
                            cumulative_sum = previous_rows['ST P/L'].cumsum()
                            max_negative_sum = cumulative_sum[cumulative_sum < supertrendLongLoss_xPercentDrawdown].min() if not cumulative_sum.empty else 0    
                            longLossDf.loc[k, 'Long Loss Entry'] = True if max_negative_sum < 0 else False

                    OriginalLongLossDf['Long Loss Entry'] =  OriginalLongLossDf['Date'].isin(longLossDf['Date']).shift(1)
                    df['Long Loss Entry'] = df['Date'].map(OriginalLongLossDf.set_index('Date')['Long Loss Entry']).fillna(False).astype(bool)
            
            if lowerHighLows_LowerHighToggle or lowerHighLows_LowerLowToggle:
                
                if lowerHighLows_LowerLowToggle:
                    pattern_columns.append('Lower_Low')
                    
                if lowerHighLows_LowerHighToggle:
                    pattern_columns.append('Lower_High')

                if lowerHighLows_AndOrToggle:
                    pattern_columns.append('Lower_Low AND Lower_High')
                
                df['Lower_Low'] = (df['Low'] < df['Low'].shift(1)).rolling(window= lowerHighLows_LowerLowDays if lowerHighLows_ConsecutiveToggle else lowerHighLows_LookBackDays).sum()==lowerHighLows_LowerLowDays
                df['Lower_High'] = (df['High'] < df['High'].shift(1)).rolling(window= lowerHighLows_LowerHighDays if lowerHighLows_ConsecutiveToggle else lowerHighLows_LookBackDays).sum()==lowerHighLows_LowerHighDays
                df['Lower_Low AND Lower_High'] = df['Lower_High'] & df['Lower_Low']

            if pattern_columns:
                mask = df[pattern_columns].any(axis=1)
                df_filtered = df[mask].copy()
                df_filtered['Candle Stick Pattern'] = df_filtered[pattern_columns].apply(lambda row: [pattern for pattern in pattern_columns if row[pattern]], axis=1)

                # Select only Date, Ticker, and Candle Stick Pattern columns
                df_filtered = df_filtered[['Date', 'Ticker', 'Candle Stick Pattern']].copy()
                df_filtered.loc[:, 'Candle Stick Pattern'] = df_filtered['Candle Stick Pattern'].apply(lambda x: ', '.join(x))

                # Filter rows by `Candle Pattern` and reference date
                if len(df_filtered) > 0:
                    df_filtered = df_filtered[(df_filtered['Date'] >= startDate) & (df_filtered['Date'] <= endDate)]
                    df_filtered['Date'] = df_filtered['Date'].dt.strftime('%d-%b-%Y')
                    candleStickPatternFinalDf = pd.concat([candleStickPatternFinalDf,df_filtered])     
        
    print("Elapsed time:", time() - startTime)
    csvFinalDf = dcc.send_data_frame(candleStickPatternFinalDf.to_csv, 'Youngturtle_MonthOnMonth.csv')    
    return candleStickPatternFinalDf.to_dict('records')

@callback(
    Output(component_id='scanner_download_csv', component_property='data'),
    Input('scanner_download_button', 'n_clicks'),
    prevent_initial_call=True
)
def monthOnMonthDataTable(
    scanner_download_button
):
    return csvFinalDf

# if __name__ == '__main__':
#     app.run_server(debug=False)