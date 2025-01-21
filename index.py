from dash import Dash, dcc, html, Input, Output, dash_table
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

from tabs.dailyTimeFrame import dailyTimeFrameLayout
from tabs.weeklyTimeFrame import weeklyTimeFrameLayout
from tabs.monthlyTimeFrame import monthlyTimeFrameLayout
from tabs.yearlyTimeFrame import yearlyTimeFrameLayout
from tabs.dailyTimeFrame_scenario import scenarioLayout
from tabs.symbolScanner import symbolScannerLayout
from tabs.phenomenaBackTester import phenomenaBackTesterLayout
from tabs.animatedCharts import animatedChartsLayout
from tabs.dailyTimeFrame_elections import dailyTimeFrameElectionLayout
from tabs.phenomena import phenomenaLayout
from tabs.candleStickPattern import candleStickpatternLayout


assets_path = os.getcwd() + '/assets'


app = Dash(__name__,
           title='Seasonality',
           assets_folder=assets_path, include_assets_files=True,
           suppress_callback_exceptions=True,
           external_stylesheets=[dbc.themes.LITERA],
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
           )


app_tabs = html.Div(
    [
        dbc.Tabs(
            id='tabs', active_tab='dailyTab',
            children=[
                dbc.Tab(label='Daily', tab_id='dailyTab',
                        labelClassName='text-blue font-weight-bold text-center', activeLabelClassName='text-black text-center',
                        label_style={'cursor': 'pointer', 'height': '50px', 'width': '125px', 'fontSize': 25},
                        tab_style={'cursor': 'pointer', 'height': '50px', 'width': '125px'}),
                dbc.Tab(label='Weekly', tab_id='weeklyTab',
                        labelClassName='text-blue font-weight-bold text-center', activeLabelClassName='text-black text-center',
                        label_style={'cursor': 'pointer', 'height': '50px', 'width': '125px', 'fontSize': 25},
                        tab_style={'cursor': 'pointer', 'height': '50px', 'width': '125px'}),
                dbc.Tab(label='Monthly', tab_id='monthlyTab',
                        labelClassName='text-blue font-weight-bold text-center', activeLabelClassName='text-black text-center',
                        label_style={'cursor': 'pointer', 'height': '50px', 'width': '125px', 'fontSize': 25},
                        tab_style={'cursor': 'pointer', 'height': '50px', 'width': '125px'}),
                dbc.Tab(label='Yearly', tab_id='yearlyTab',
                        labelClassName='text-blue font-weight-bold text-center', activeLabelClassName='text-black text-center',
                        label_style={'cursor': 'pointer', 'height': '50px', 'width': '125px', 'fontSize': 25},
                        tab_style={'cursor': 'pointer', 'height': '50px', 'width': '125px'}),
                dbc.Tab(label='Scenario', tab_id='scenarioTab',
                        labelClassName='text-blue font-weight-bold text-center', activeLabelClassName='text-black text-center',
                        label_style={'cursor': 'pointer', 'height': '50px', 'width': '135px', 'fontSize': 25},
                        tab_style={'cursor': 'pointer', 'height': '50px', 'width': '135px'}),
                dbc.Tab(label='Elections', tab_id='electionTab',
                        labelClassName='text-blue font-weight-bold text-center', activeLabelClassName='text-black text-center',
                        label_style={'cursor': 'pointer', 'height': '50px', 'width': '135px', 'fontSize': 25,  },
                        tab_style={'cursor': 'pointer', 'height': '50px', 'width': '135px'}), 
                dbc.Tab(label='Scanner', tab_id='scannerTab',
                        labelClassName='text-blue font-weight-bold text-center', activeLabelClassName='text-black text-center',
                        label_style={'cursor': 'pointer', 'height': '50px', 'width': '135px', 'fontSize': 25, },
                        tab_style={'cursor': 'pointer', 'height': '50px', 'width': '135px'}),
                dbc.Tab(label='Phenomena Backtester', tab_id='phenomenaBackTesterTab',
                        labelClassName='text-blue font-weight-bold text-center', activeLabelClassName='text-black text-center',
                        label_style={'cursor': 'pointer', 'height': '50px', 'width': '320px', 'fontSize': 25,  },
                        tab_style={'cursor': 'pointer', 'height': '50px', 'width': '320px'}),
                dbc.Tab(label='Phenomena', tab_id='phenomenaTab',
                        labelClassName='text-blue font-weight-bold text-center', activeLabelClassName='text-black text-center',
                        label_style={'cursor': 'pointer', 'height': '50px', 'width': '150px', 'fontSize': 25},
                        tab_style={'cursor': 'pointer', 'height': '50px', 'width': '150px'}), 
                dbc.Tab(label='Animated Charts', tab_id='animatedChartsTab',
                        labelClassName='text-blue font-weight-bold text-center', activeLabelClassName='text-black text-center',
                        label_style={'cursor': 'pointer', 'height': '50px', 'width': '230px', 'fontSize': 25, },
                        tab_style={'cursor': 'pointer', 'height': '50px', 'width': '230px'}),       

                dbc.Tab(label='CandleStick Pattern', tab_id='candlestick',
                        labelClassName='text-blue font-weight-bold text-center', activeLabelClassName='text-black text-center',
                        label_style={'cursor': 'pointer', 'height': '50px', 'width': '230px', 'fontSize': 25, },
                        tab_style={'cursor': 'pointer', 'height': '50px', 'width': '230px'}),       
            ],
            style={'height': 50, 'fontWeight': 'bold', 'borderBottom': '2px solid lightblue'},
            persistence=True, persistence_type='session'
        ),
    ]
)


app.layout = html.Div([
    html.Br(),
    dbc.Row(dbc.Col(app_tabs, width=50)),
    html.Div(id='content', children=[])
],
    style={'width': '99%', 'zoom': '100%'}
)


@app.callback(
    Output('content', 'children'),
    Input('tabs', 'active_tab')
)
def switch_tab(tab_chosen):
    if (tab_chosen == 'dailyTab'):
        return dailyTimeFrameLayout
    elif (tab_chosen == 'weeklyTab'):
        return weeklyTimeFrameLayout
    elif (tab_chosen == 'monthlyTab'):
        return monthlyTimeFrameLayout
    elif (tab_chosen == 'yearlyTab'):
        return yearlyTimeFrameLayout
    elif (tab_chosen == 'scenarioTab'):
        return scenarioLayout
    elif (tab_chosen == 'scannerTab'):
        return symbolScannerLayout
    elif (tab_chosen == 'phenomenaBackTesterTab'):
        return phenomenaBackTesterLayout
    elif (tab_chosen == 'animatedChartsTab'):
        return animatedChartsLayout
    elif(tab_chosen=='electionTab'):
        return dailyTimeFrameElectionLayout
    elif(tab_chosen=='phenomenaTab'):
        return phenomenaLayout
    elif(tab_chosen=='candlestick'):
        return candleStickpatternLayout
    
if __name__ == '__main__':
    app.run_server(debug=False)
