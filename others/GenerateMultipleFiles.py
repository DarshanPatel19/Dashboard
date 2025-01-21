import os
import glob
import pandas as pd
import numpy as np
import math
import csv
from datetime import datetime, timedelta
import re
import shutil
from time import sleep


columnLogic = {
    'Ticker': 'first',
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum',
    'OpenInterest': 'last',
    'Weekday': 'first'
}


symbolMondayWeeklyData = pd.DataFrame()
symbolExpiryWeeklyData = pd.DataFrame()
symbolMonthlyData = pd.DataFrame()
symbolYearlyData = pd.DataFrame()


def getYearlyReturns(row):
    global symbolYearlyData
    yearlyReturns = [np.nan, np.nan]
    yearlyRow = symbolYearlyData[symbolYearlyData['Date'] == datetime(row['Date'].year, 1, 1)]
    if (len(yearlyRow) > 0):
        yearlyReturnPoints = yearlyRow['ReturnPoints'].iloc[0]
        yearlyReturnPercentage = yearlyRow['ReturnPercentage'].iloc[0]
        yearlyReturns[0] = yearlyReturnPoints
        yearlyReturns[1] = yearlyReturnPercentage
    return yearlyReturns


def getMonthlyReturns(row):
    global symbolMonthlyData
    monthlyReturns = [np.nan, np.nan]
    monthlyRow = symbolMonthlyData[symbolMonthlyData['Date'] == datetime(row['Date'].year, row['Date'].month, 1)]
    if (len(monthlyRow) > 0):
        monthlyReturnPoints = monthlyRow['ReturnPoints'].iloc[0]
        monthlyReturnPercentage = monthlyRow['ReturnPercentage'].iloc[0]
        monthlyReturns[0] = monthlyReturnPoints
        monthlyReturns[1] = monthlyReturnPercentage
    return monthlyReturns


def getMondayWeeklyData(row):
    global symbolMondayWeeklyData
    mondayWeeklyData = [np.nan, np.nan, np.nan, np.nan]
    mondayRow = symbolMondayWeeklyData[symbolMondayWeeklyData['Date'] == row['MondayWeeklyDate']]
    if (len(mondayRow) > 0):
        mondayWeeklyReturnPoints = mondayRow['ReturnPoints'].iloc[0]
        mondayWeeklyReturnPercentage = mondayRow['ReturnPercentage'].iloc[0]
        mondayWeekNumberMonthly = mondayRow['WeekNumberMonthly'].iloc[0]
        mondayWeekNumberYearly = mondayRow['WeekNumberYearly'].iloc[0]
        mondayWeeklyData[0] = mondayWeeklyReturnPoints
        mondayWeeklyData[1] = mondayWeeklyReturnPercentage
        mondayWeeklyData[2] = mondayWeekNumberMonthly
        mondayWeeklyData[3] = mondayWeekNumberYearly
    return mondayWeeklyData


def getExpiryWeeklyData(row):
    global symbolExpiryWeeklyData
    expiryWeeklyData = [np.nan, np.nan, np.nan, np.nan]
    expiryRow = symbolExpiryWeeklyData[symbolExpiryWeeklyData['Date'] == row['ExpiryWeeklyDate']]
    if (len(expiryRow) > 0):
        expiryWeeklyReturnPoints = expiryRow['ReturnPoints'].iloc[0]
        expiryWeeklyReturnPercentage = expiryRow['ReturnPercentage'].iloc[0]
        expiryWeekNumberMonthly = expiryRow['WeekNumberMonthly'].iloc[0]
        expiryWeekNumberYearly = expiryRow['WeekNumberYearly'].iloc[0]
        expiryWeeklyData[0] = expiryWeeklyReturnPoints
        expiryWeeklyData[1] = expiryWeeklyReturnPercentage
        expiryWeeklyData[2] = expiryWeekNumberMonthly
        expiryWeeklyData[3] = expiryWeekNumberYearly
    return expiryWeeklyData


def generateFiles(symbolDailyData, fileStorePath):

    global symbolMondayWeeklyData
    global symbolExpiryWeeklyData
    global symbolMonthlyData
    global symbolYearlyData

    # Read Daily data file and format columns
    print('Daily data file and format columns')
    symbolDailyData['Date'] = pd.to_datetime(symbolDailyData['Date'], format='%d-%m-%Y')
    symbolDailyData['Weekday'] = symbolDailyData['Date'].dt.day_name()
    symbolDailyData = symbolDailyData.set_index('Date').sort_index(ascending=True)
    print('Done')

    # Convert daily to weekly timeframe from monday as start of week
    print('Convert daily to weekly timeframe from monday as start of week')
    symbolMondayWeeklyData = symbolDailyData.resample('W-SUN').apply(columnLogic).reset_index()
    symbolMondayWeeklyData['Date'] = symbolMondayWeeklyData['Date'] - pd.tseries.frequencies.to_offset("6D")
    symbolMondayWeeklyData['Weekday'] = symbolMondayWeeklyData['Date'].dt.day_name()
    symbolMondayWeeklyData = symbolMondayWeeklyData.set_index('Date').sort_index(ascending=True)
    print('Done')

    # Convert daily to weekly timeframe from expiry week and friday as start of week
    print('Convert daily to weekly timeframe from expiry week and friday as start of week')
    symbolExpiryWeeklyData = symbolDailyData.resample('W-THU').apply(columnLogic).reset_index()
    symbolExpiryWeeklyData['StartDate'] = symbolExpiryWeeklyData['Date'] - pd.tseries.frequencies.to_offset("6D")
    symbolExpiryWeeklyData['Weekday'] = symbolExpiryWeeklyData['Date'].dt.day_name()
    symbolExpiryWeeklyData = symbolExpiryWeeklyData.set_index('Date').sort_index(ascending=True)
    print('Done')

    # Convert daily to monthly timeframe
    print('Convert daily to monthly timeframe')
    symbolMonthlyData = symbolDailyData.resample('M').apply(columnLogic).reset_index()
    symbolMonthlyData['Date'] = pd.to_datetime(symbolMonthlyData['Date'].dt.strftime('%m-%Y'))
    symbolMonthlyData['Weekday'] = symbolMonthlyData['Date'].dt.day_name()
    symbolMonthlyData = symbolMonthlyData.set_index('Date').sort_index(ascending=True)
    print('Done')

    # Convert daily to yearly timeframe
    print('Convert daily to yearly timeframe')
    symbolYearlyData = symbolDailyData.resample('Y').apply(columnLogic).reset_index()
    symbolYearlyData['Date'] = pd.to_datetime(symbolYearlyData['Date'].dt.strftime('%Y'))
    symbolYearlyData['Weekday'] = symbolYearlyData['Date'].dt.day_name()
    symbolYearlyData = symbolYearlyData.set_index('Date').sort_index(ascending=True)
    print('Done')

    # Reset all dataframe indices
    symbolDailyData.reset_index(inplace=True)
    symbolMondayWeeklyData.reset_index(inplace=True)
    symbolExpiryWeeklyData.reset_index(inplace=True)
    symbolMonthlyData.reset_index(inplace=True)
    symbolYearlyData.reset_index(inplace=True)

    # generate new fields of yearly data
    print('Generate new fields of yearly data')
    symbolYearlyData['EvenYear'] = ((symbolYearlyData['Date'].dt.year % 2) == 0)
    symbolYearlyData['ReturnPoints'] = symbolYearlyData['Close'] - symbolYearlyData['Close'].shift(1)
    symbolYearlyData['ReturnPercentage'] = round((symbolYearlyData['ReturnPoints'] / symbolYearlyData['Close'].shift(1)*100), 2)
    symbolYearlyData['PositiveYear'] = (symbolYearlyData['ReturnPoints'] > 0)
    print('Done')

    # generate new fields of monthly data
    print('Generate new fields of monthly data')
    symbolMonthlyData['EvenMonth'] = ((symbolMonthlyData['Date'].dt.month % 2) == 0)
    symbolMonthlyData['ReturnPoints'] = symbolMonthlyData['Close'] - symbolMonthlyData['Close'].shift(1)
    symbolMonthlyData['ReturnPercentage'] = round((symbolMonthlyData['ReturnPoints'] / symbolMonthlyData['Close'].shift(1)*100), 2)
    symbolMonthlyData['PositiveMonth'] = (symbolMonthlyData['ReturnPoints'] > 0)

    yearlyReturns = np.array(symbolMonthlyData.apply(lambda row: getYearlyReturns(row), axis=1).tolist()).transpose()
    symbolMonthlyData['EvenYear'] = ((symbolMonthlyData['Date'].dt.year % 2) == 0)
    symbolMonthlyData['YearlyReturnPoints'], symbolMonthlyData['YearlyReturnPercentage'] = yearlyReturns[0], yearlyReturns[1]
    symbolMonthlyData['PositiveYear'] = (symbolMonthlyData['YearlyReturnPoints'] > 0)
    print('Done')

    # generate new fields of monday weekly data
    print('Generate new fields of monday weekly data')
    symbolMondayWeeklyData['WeekNumberMonthly'] = symbolMondayWeeklyData['WeekNumberYearly'] = np.nan

    for i in range(1, len(symbolMondayWeeklyData)):
        if (symbolMondayWeeklyData.loc[i, 'Date'].month != symbolMondayWeeklyData.loc[i-1, 'Date'].month):
            symbolMondayWeeklyData.loc[i, 'WeekNumberMonthly'] = 1
        else:
            symbolMondayWeeklyData.loc[i, 'WeekNumberMonthly'] = symbolMondayWeeklyData.loc[i-1, 'WeekNumberMonthly'] + 1
        if (symbolMondayWeeklyData.loc[i, 'Date'].year != symbolMondayWeeklyData.loc[i-1, 'Date'].year):
            symbolMondayWeeklyData.loc[i, 'WeekNumberYearly'] = 1
        else:
            symbolMondayWeeklyData.loc[i, 'WeekNumberYearly'] = symbolMondayWeeklyData.loc[i-1, 'WeekNumberYearly'] + 1

    symbolMondayWeeklyData['EvenWeekNumberMonthly'] = ((symbolMondayWeeklyData['WeekNumberMonthly'] % 2) == 0)
    symbolMondayWeeklyData['EvenWeekNumberYearly'] = ((symbolMondayWeeklyData['WeekNumberYearly'] % 2) == 0)
    symbolMondayWeeklyData[['WeekNumberMonthly', 'WeekNumberYearly']] = symbolMondayWeeklyData[
        ['WeekNumberMonthly', 'WeekNumberYearly']
    ].fillna(value=0).astype('Int64').replace(0, np.nan)

    symbolMondayWeeklyData['ReturnPoints'] = symbolMondayWeeklyData['Close'] - symbolMondayWeeklyData['Close'].shift(1)
    symbolMondayWeeklyData['ReturnPercentage'] = round((symbolMondayWeeklyData['ReturnPoints'] / symbolMondayWeeklyData['Close'].shift(1)*100), 2)
    symbolMondayWeeklyData['PositiveWeek'] = (symbolMondayWeeklyData['ReturnPoints'] > 0)

    monthlyReturns = np.array(symbolMondayWeeklyData.apply(lambda row: getMonthlyReturns(row), axis=1).tolist()).transpose()
    symbolMondayWeeklyData['EvenMonth'] = ((symbolMondayWeeklyData['Date'].dt.month % 2) == 0)
    symbolMondayWeeklyData['MonthlyReturnPoints'], symbolMondayWeeklyData['MonthlyReturnPercentage'] = monthlyReturns[0], monthlyReturns[1]
    symbolMondayWeeklyData['PositiveMonth'] = (symbolMondayWeeklyData['MonthlyReturnPoints'] > 0)

    yearlyReturns = np.array(symbolMondayWeeklyData.apply(lambda row: getYearlyReturns(row), axis=1).tolist()).transpose()
    symbolMondayWeeklyData['EvenYear'] = ((symbolMondayWeeklyData['Date'].dt.year % 2) == 0)
    symbolMondayWeeklyData['YearlyReturnPoints'], symbolMondayWeeklyData['YearlyReturnPercentage'] = yearlyReturns[0], yearlyReturns[1]
    symbolMondayWeeklyData['PositiveYear'] = (symbolMondayWeeklyData['YearlyReturnPoints'] > 0)
    print('Done')

    # generate new fields of friday weekly data
    print('Generate new fields of friday weekly data')
    symbolExpiryWeeklyData['WeekNumberMonthly'] = symbolExpiryWeeklyData['WeekNumberYearly'] = np.nan

    for i in range(1, len(symbolExpiryWeeklyData)):
        if (symbolExpiryWeeklyData.loc[i, 'Date'].month != symbolExpiryWeeklyData.loc[i-1, 'Date'].month):
            symbolExpiryWeeklyData.loc[i, 'WeekNumberMonthly'] = 1
        else:
            symbolExpiryWeeklyData.loc[i, 'WeekNumberMonthly'] = symbolExpiryWeeklyData.loc[i-1, 'WeekNumberMonthly'] + 1
        if (symbolExpiryWeeklyData.loc[i, 'Date'].year != symbolExpiryWeeklyData.loc[i-1, 'Date'].year):
            symbolExpiryWeeklyData.loc[i, 'WeekNumberYearly'] = 1
        else:
            symbolExpiryWeeklyData.loc[i, 'WeekNumberYearly'] = symbolExpiryWeeklyData.loc[i-1, 'WeekNumberYearly'] + 1

    symbolExpiryWeeklyData['EvenWeekNumberMonthly'] = ((symbolExpiryWeeklyData['WeekNumberMonthly'] % 2) == 0)
    symbolExpiryWeeklyData['EvenWeekNumberYearly'] = ((symbolExpiryWeeklyData['WeekNumberYearly'] % 2) == 0)
    symbolExpiryWeeklyData[['WeekNumberMonthly', 'WeekNumberYearly']] = symbolExpiryWeeklyData[
        ['WeekNumberMonthly', 'WeekNumberYearly']
    ].fillna(value=0).astype('Int64').replace(0, np.nan)

    symbolExpiryWeeklyData['ReturnPoints'] = symbolExpiryWeeklyData['Close'] - symbolExpiryWeeklyData['Close'].shift(1)
    symbolExpiryWeeklyData['ReturnPercentage'] = round((symbolExpiryWeeklyData['ReturnPoints']/symbolExpiryWeeklyData['Close'].shift(1)*100), 2)
    symbolExpiryWeeklyData['PositiveWeek'] = (symbolExpiryWeeklyData['ReturnPoints'] > 0)

    monthlyReturns = np.array(symbolExpiryWeeklyData.apply(lambda row: getMonthlyReturns(row), axis=1).tolist()).transpose()
    symbolExpiryWeeklyData['EvenMonth'] = ((symbolExpiryWeeklyData['Date'].dt.month % 2) == 0)
    symbolExpiryWeeklyData['MonthlyReturnPoints'], symbolExpiryWeeklyData['MonthlyReturnPercentage'] = monthlyReturns[0], monthlyReturns[1]
    symbolExpiryWeeklyData['PositiveMonth'] = (symbolExpiryWeeklyData['MonthlyReturnPoints'] > 0)

    yearlyReturns = np.array(symbolExpiryWeeklyData.apply(lambda row: getYearlyReturns(row), axis=1).tolist()).transpose()
    symbolExpiryWeeklyData['EvenYear'] = ((symbolExpiryWeeklyData['Date'].dt.year % 2) == 0)
    symbolExpiryWeeklyData['YearlyReturnPoints'], symbolExpiryWeeklyData['YearlyReturnPercentage'] = yearlyReturns[0], yearlyReturns[1]
    symbolExpiryWeeklyData['PositiveYear'] = (symbolExpiryWeeklyData['YearlyReturnPoints'] > 0)
    print('Done')

    # generate new fields of daily data
    print('Generate new fields of daily data')
    symbolDailyData['CalenderMonthDay'] = symbolDailyData['Date'].dt.day
    symbolDailyData['CalenderYearDay'] = symbolDailyData['Date'].dt.dayofyear
    symbolDailyData['TradingMonthDay'] = symbolDailyData['TradingYearDay'] = np.nan

    for i in range(1, len(symbolDailyData)):
        if (symbolDailyData.loc[i, 'Date'].month != symbolDailyData.loc[i-1, 'Date'].month):
            symbolDailyData.loc[i, 'TradingMonthDay'] = 1
        else:
            symbolDailyData.loc[i, 'TradingMonthDay'] = symbolDailyData.loc[i - 1, 'TradingMonthDay'] + 1
        if (symbolDailyData.loc[i, 'Date'].year != symbolDailyData.loc[i-1, 'Date'].year):
            symbolDailyData.loc[i, 'TradingYearDay'] = 1
        else:
            symbolDailyData.loc[i, 'TradingYearDay'] = symbolDailyData.loc[i - 1, 'TradingYearDay'] + 1

    symbolDailyData['EvenCalenderMonthDay'] = ((symbolDailyData['CalenderMonthDay'] % 2) == 0)
    symbolDailyData['EvenCalenderYearDay'] = ((symbolDailyData['CalenderYearDay'] % 2) == 0)
    symbolDailyData['EvenTradingMonthDay'] = ((symbolDailyData['TradingMonthDay'] % 2) == 0)
    symbolDailyData['EvenTradingYearDay'] = ((symbolDailyData['TradingYearDay'] % 2) == 0)

    symbolDailyData[['TradingMonthDay', 'TradingYearDay']] = symbolDailyData[
        ['TradingMonthDay', 'TradingYearDay']
    ].fillna(value=0).astype('Int64').replace(0, np.nan)

    symbolDailyData['ReturnPoints'] = symbolDailyData['Close'] - symbolDailyData['Close'].shift(1)
    symbolDailyData['ReturnPercentage'] = round((symbolDailyData['ReturnPoints'] / symbolDailyData['Close'].shift(1)*100), 2)
    symbolDailyData['PositiveDay'] = (symbolDailyData['ReturnPoints'] > 0)

    # weekly monday calculations
    symbolDailyData['MondayWeeklyDate'] = symbolDailyData['Date'].apply(lambda x: x - pd.tseries.frequencies.to_offset(str(x.weekday()) + 'D'))
    mondayWeeklyData = np.array(symbolDailyData.apply(lambda row: getMondayWeeklyData(row), axis=1).tolist()).transpose()

    symbolDailyData['MondayWeekNumberMonthly'] = symbolDailyData['MondayWeekNumberYearly'] = np.nan
    symbolDailyData['MondayWeekNumberMonthly'], symbolDailyData['MondayWeekNumberYearly'], \
        symbolDailyData['EvenMondayWeekNumberMonthly'], symbolDailyData['EvenMondayWeekNumberYearly'], \
        symbolDailyData['MondayWeeklyReturnPoints'], symbolDailyData['MondayWeeklyReturnPercentage'], \
        symbolDailyData['PositiveMondayWeek'] = \
        mondayWeeklyData[2], mondayWeeklyData[3], \
        ([((i % 2) == 0) for i in mondayWeeklyData[2]]), ([((i % 2) == 0) for i in mondayWeeklyData[3]]), \
        mondayWeeklyData[0], mondayWeeklyData[1], \
        ([(i > 0) for i in mondayWeeklyData[0]])

    # weekly friday calculations
    symbolDailyData['ExpiryWeeklyDate'] = symbolDailyData['Date'].apply(
        lambda x: (x + pd.tseries.frequencies.to_offset(str(6) + 'D')) if (x.weekday() == 4)
        else (x + pd.tseries.frequencies.to_offset(str(3-x.weekday()) + 'D'))
    )
    expiryWeeklyData = np.array(symbolDailyData.apply(lambda row: getExpiryWeeklyData(row), axis=1).tolist()).transpose()

    symbolDailyData['ExpiryWeekNumberMonthly'] = symbolDailyData['ExpiryWeekNumberYearly'] = np.nan
    symbolDailyData['ExpiryWeekNumberMonthly'], symbolDailyData['ExpiryWeekNumberYearly'], \
        symbolDailyData['EvenExpiryWeekNumberMonthly'], symbolDailyData['EvenExpiryWeekNumberYearly'], \
        symbolDailyData['ExpiryWeeklyReturnPoints'], symbolDailyData['ExpiryWeeklyReturnPercentage'], \
        symbolDailyData['PositiveExpiryWeek'] = \
        expiryWeeklyData[2], expiryWeeklyData[3], \
        ([((i % 2) == 0) for i in expiryWeeklyData[2]]), ([((i % 2) == 0) for i in expiryWeeklyData[3]]), \
        expiryWeeklyData[0], expiryWeeklyData[1], \
        ([(i > 0) for i in expiryWeeklyData[0]])

    # replace not a number values in data frame
    symbolDailyData[['MondayWeekNumberMonthly', 'MondayWeekNumberYearly']] = symbolDailyData[
        ['MondayWeekNumberMonthly', 'MondayWeekNumberYearly']
    ].fillna(value=0).astype('Int64').replace(0, np.nan)
    symbolDailyData[['ExpiryWeekNumberMonthly', 'ExpiryWeekNumberYearly']] = symbolDailyData[
        ['ExpiryWeekNumberMonthly', 'ExpiryWeekNumberYearly']
    ].fillna(value=0).astype('Int64').replace(0, np.nan)

    # monthly data calculation
    monthlyReturns = np.array(symbolDailyData.apply(lambda row: getMonthlyReturns(row), axis=1).tolist()).transpose()
    symbolDailyData['EvenMonth'] = ((symbolDailyData['Date'].dt.month % 2) == 0)
    symbolDailyData['MonthlyReturnPoints'], symbolDailyData['MonthlyReturnPercentage'] = monthlyReturns[0], monthlyReturns[1]
    symbolDailyData['PositiveMonth'] = (symbolDailyData['MonthlyReturnPoints'] > 0)

    # yearly data calculation
    yearlyReturns = np.array(symbolDailyData.apply(lambda row: getYearlyReturns(row), axis=1).tolist()).transpose()
    symbolDailyData['EvenYear'] = ((symbolDailyData['Date'].dt.year % 2) == 0)
    symbolDailyData['YearlyReturnPoints'], symbolDailyData['YearlyReturnPercentage'] = yearlyReturns[0], yearlyReturns[1]
    symbolDailyData['PositiveYear'] = (symbolDailyData['YearlyReturnPoints'] > 0)
    print('Done')

    # save all files to csv
    print('Save all files to csv')
    symbolDailyData.set_index('Date').to_csv(fileStorePath + '1_Daily.csv')
    symbolMondayWeeklyData.set_index('Date').to_csv(fileStorePath + '2_MondayWeekly.csv')
    symbolExpiryWeeklyData.set_index('Date').to_csv(fileStorePath + '3_ExpiryWeekly.csv')
    symbolMonthlyData.set_index('Date').to_csv(fileStorePath + '4_Monthly.csv')
    symbolYearlyData.set_index('Date').to_csv(fileStorePath + '5_Yearly.csv')
    print('Done')


"""
    Main code logic starts
"""


symbolsFolderPath = './Symbols'
count = 0

if not (os.path.exists(symbolsFolderPath)):
    os.makedirs(symbolsFolderPath)

dataFile = pd.read_csv('./Seasonality.csv')
dataFile = dataFile.astype({
    'Ticker': str,
    'Open': np.float64,
    'High': np.float64,
    'Low': np.float64,
    'Close': np.float64,
    'Volume': np.int64,
    'OpenInterest': np.int64
})
dataFile['Date'] = pd.to_datetime(dataFile['Date'], format='%Y-%m-%d')
symbols_sorted_data = dataFile.groupby(['Ticker'], group_keys=False).apply(lambda x: x.sort_values(
    ['Date'], ascending=True)).reset_index(drop=True)

print('\nTotal symbols : ', len(symbols_sorted_data['Ticker'].unique()))
print('---------------------------------------------------------------------------------------------')


for ticker in (symbols_sorted_data['Ticker'].unique()):

    count = count + 1
    print(count, ticker)

    tickerData = symbols_sorted_data[symbols_sorted_data['Ticker'] == ticker]
    if ((tickerData.iloc[0]['Date'].day) < 8):
        tickerData = tickerData.iloc[(8 - (tickerData.iloc[0]['Date'].day)):]
    tickerData['Date'] = tickerData['Date'].dt.strftime('%d-%m-%Y')
    filePath = symbolsFolderPath + '//' + ticker + '//'

    if not (os.path.exists(filePath)):
        os.makedirs(filePath)

    generateFiles(tickerData, filePath)

    print('---------------------------------------------------------------------------------------------')
