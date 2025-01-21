from dash import Dash, dcc, html, Input, Output, dash_table
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os
from dateutil.relativedelta import relativedelta
import time

symbolNamesToDropdown = next(os.walk('./Symbols'))[1]
watchListToDropDown = pd.read_csv('./Watchlist/Watchlist.csv').columns.to_list()
electionInfoDf = pd.read_csv('./elections/ElectionDates.csv')
specialDaysToDropdown = list(map(str.upper, pd.read_csv('./SpecialDays/SpecialDays.csv').columns))
weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
tradingDays = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
calenderDays = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
monthFullNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
MaincolorDict = {'All Years' : '#000000','Election Years' : '#000000','Post Election Years' : '#008000','Pre Election Years' : '#FF0000','Mid Election Years' : '#0000FF','Modi Years' : '#FF00FF','Current Year' : '#AD0AFD',}
colorDict = {}
monthDict = {'All Months': 0,'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
hoverElecList = {'All Years':' - All Years','Election Years': ' Election','Pre Election Years': ' Pre Election','Post Election Years': ' Post Election','Mid Election Years': ' Mid Election','Current Year': ' Curr Year','Modi Years': ' Modi Years'}
lineStyleElecList = {'All Years':'solid','Election Years': 'dot','Pre Election Years': 'solid','Post Election Years': 'solid','Mid Election Years': 'solid','Modi Years': 'solid','Current Year': '1px 1px'}
electionDateList = {1952,1957,1962,1967,1971,1977,1980,1984,1989,1991,1996,1998,1999,2004,2009,2014,2019}
SecondaryColorList = ['#888888',
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#1a1a1a', '#ff5733', '#33ff57', '#337aff', '#ff33cc',
    '#ffe333', '#3333ff', '#9933ff', '#ff3333', '#33ffcc'
    ]

def getDataTableStatistics(allDayReturnPoints1):
    positiveReturnPoints1 = allDayReturnPoints1[allDayReturnPoints1 > 0]
    negativeReturnPoints1 = allDayReturnPoints1[allDayReturnPoints1 < 0]
    allDaysStats = pd.Series({
        'All Count': np.size(allDayReturnPoints1) if np.size(allDayReturnPoints1) > 0 else 0,
        'Average Return of All': np.mean(allDayReturnPoints1) if np.size(allDayReturnPoints1) > 0 else 0,
        'Sum Return of All': np.sum(allDayReturnPoints1) if np.size(allDayReturnPoints1) > 0 else 0,
        'Positive Count': np.size(positiveReturnPoints1) if np.size(positiveReturnPoints1) > 0 else 0,
        'Average Return of Positive': np.mean(positiveReturnPoints1) if np.size(positiveReturnPoints1) > 0 else 0,
        'Sum Return of Positive': np.sum(positiveReturnPoints1) if np.size(positiveReturnPoints1) > 0 else 0,
        'Negative Count': np.size(negativeReturnPoints1) if np.size(negativeReturnPoints1) > 0 else 0,
        'Average Return of Negative': np.mean(negativeReturnPoints1) if np.size(negativeReturnPoints1) > 0 else 0,
        'Sum Return of Negative': np.sum(negativeReturnPoints1) if np.size(negativeReturnPoints1) > 0 else 0
    })
    return allDaysStats


def getAccuracy(row, countType):
    if (row['All Count'] == 0):
        newRow = 0
    else:
        newRow = str(int(row[countType])) + '(' + str(round(row[countType]/row['All Count']*100, 2)) + '%)'
    return newRow


def getDataTableForPlot(dataTabel1):
    dataTabel1 = dataTabel1.T
    dataTabel1 = dataTabel1.astype({
        'All Count': np.int64, 'Average Return of All': np.float64, 'Sum Return of All': np.float64,
        'Positive Count': np.int64, 'Average Return of Positive': np.float64, 'Sum Return of Positive': np.float64,
        'Negative Count': np.int64, 'Average Return of Negative': np.float64, 'Sum Return of Negative': np.float64
    })
    dataTabel1[[
        'Average Return of All', 'Average Return of Positive', 'Average Return of Negative',
        'Sum Return of All', 'Sum Return of Positive', 'Sum Return of Negative'
    ]] = dataTabel1[[
        'Average Return of All', 'Average Return of Positive', 'Average Return of Negative',
        'Sum Return of All', 'Sum Return of Positive', 'Sum Return of Negative'
    ]].round(decimals=2)
    dataTabel1['Positive Count'] = dataTabel1.apply(lambda x: getAccuracy(x, 'Positive Count'), axis=1)
    dataTabel1['Negative Count'] = dataTabel1.apply(lambda x: getAccuracy(x, 'Negative Count'), axis=1)
    dataTabelTemp = dataTabel1.copy(deep=True)
    dataTabel1 = dataTabel1.reset_index()
    dataTabel1 = dataTabel1.to_dict('records')
    return [dataTabel1, dataTabelTemp]


def getNConsecutiveSequanceIndexFromList(
    _dayDataTable, _trendTypeValue, _consecutiveTrendingDaysValue,
    _minimumAccuracyOfEachDayValue, _minimumTotalPnlOfAllTrendingDaysValue,
    _minimumSampleSizeValue, _minimumAveragePnlOfEachTrendingDaysValue,
    _input12operationValue, _input23operationValue, _input34operationValue
):

    _sumReturnOfAll = _dayDataTable['Sum Return of All'].to_list()
    _accuracyOfAll = _dayDataTable['Positive Accuracy'].to_list() if (_trendTypeValue == 'Bullish') else _dayDataTable['Negative Accuracy'].to_list()
    _sampleCountOfAll = _dayDataTable['All Count'].to_list()
    _averagePnLOfAll = _dayDataTable['Average Return of All'].to_list()

    trendTypeMultiplier = 1 if (_trendTypeValue == 'Bullish') else -1
    _sumReturnValueChunks = []
    _sumReturnIndexChunks = []

    idx = 0
    traverseTill = len(_sumReturnOfAll)-_consecutiveTrendingDaysValue

    while (idx <= traverseTill):
        advancedQueryCheck, checkChunkValues = False, False
        if ((_sumReturnOfAll[idx]*trendTypeMultiplier) > 0):
            checkChunkValues = (
                all((num*trendTypeMultiplier) > 0 for num in _sumReturnOfAll[idx:(idx+_consecutiveTrendingDaysValue)])
            )
            if (checkChunkValues):
                minimumAccuracyCheck = all(
                    num > _minimumAccuracyOfEachDayValue for num in _accuracyOfAll[idx:(idx+_consecutiveTrendingDaysValue)]
                )
                totalOfAveragePnLCheck = _minimumTotalPnlOfAllTrendingDaysValue < (sum(_averagePnLOfAll[idx:(idx+_consecutiveTrendingDaysValue)])*trendTypeMultiplier)
                minimumSampleSizeCheck = all(
                    num > _minimumSampleSizeValue for num in _sampleCountOfAll[idx:(idx+_consecutiveTrendingDaysValue)]
                )
                individualPnLCheck = all(
                    num > _minimumAveragePnlOfEachTrendingDaysValue for num in _averagePnLOfAll[idx:(idx+_consecutiveTrendingDaysValue)]
                )
                advancedQueryCheck = (minimumAccuracyCheck | totalOfAveragePnLCheck) if (_input12operationValue == 'OR') else (minimumAccuracyCheck & totalOfAveragePnLCheck)
                advancedQueryCheck = (advancedQueryCheck | minimumSampleSizeCheck) if (_input23operationValue == 'OR') else (advancedQueryCheck & minimumSampleSizeCheck)
                advancedQueryCheck = (advancedQueryCheck | individualPnLCheck) if (_input34operationValue == 'OR') else (advancedQueryCheck & individualPnLCheck)
        if (checkChunkValues & advancedQueryCheck):
            _sumReturnValueChunks = [*_sumReturnValueChunks, _sumReturnOfAll[idx:(idx+_consecutiveTrendingDaysValue)]]
            _sumReturnIndexChunks = [*_sumReturnIndexChunks, [idx, idx+_consecutiveTrendingDaysValue-1]]
            idx = idx + _consecutiveTrendingDaysValue
        else:
            idx = idx + 1

    return _sumReturnIndexChunks


def getMonthNumber(_monthFullName):
    _monthNumner = 0
    if _monthFullName == 'January':
        _monthNumner = 1
    elif _monthFullName == 'February':
        _monthNumner = 2
    elif _monthFullName == 'March':
        _monthNumner = 3
    elif _monthFullName == 'April':
        _monthNumner = 4
    elif _monthFullName == 'May':
        _monthNumner = 5
    elif _monthFullName == 'June':
        _monthNumner = 6
    elif _monthFullName == 'July':
        _monthNumner = 7
    elif _monthFullName == 'August':
        _monthNumner = 8
    elif _monthFullName == 'September':
        _monthNumner = 9
    elif _monthFullName == 'October':
        _monthNumner = 10
    elif _monthFullName == 'November':
        _monthNumner = 11
    elif _monthFullName == 'December':
        _monthNumner = 12
    return _monthNumner


def maximumConsecutiveValues(arr):
    maximumPositiveCount = 0
    currentPositiveCount = 0
    maximumNegativeCount = 0
    currentNegativeCount = 0
    for num in arr:
        if num > 0:
            currentPositiveCount += 1
            maximumPositiveCount = max(maximumPositiveCount, currentPositiveCount)
            currentNegativeCount = 0
        elif num < 0:
            currentNegativeCount += 1
            maximumNegativeCount = max(maximumNegativeCount, currentNegativeCount)
            currentPositiveCount = 0
        else:
            currentPositiveCount = 0
            currentNegativeCount = 0
    return maximumPositiveCount, maximumNegativeCount


def getHistoricTrendingDays(listValues, _historicTrendType, _historicTrendConsecutiveDays, _historicTrendDayRange):
    index, consecutiveValuesIndex = _historicTrendDayRange, 0
    trendMultiplier = 1 if _historicTrendType == 'Bullish' else -1
    listValuesIndex = [0]*len(listValues)
    consecutiveValuesIndexList = [i for i in range(1, _historicTrendConsecutiveDays+1)]

    while (index <= (len(listValues)-_historicTrendDayRange-1)):
        if ((trendMultiplier*listValues[index]) > 0):
            consecutiveValuesIndex = consecutiveValuesIndex + 1
            if (consecutiveValuesIndex == _historicTrendConsecutiveDays):
                consecutiveValuesIndex = 0
                listValuesIndex[index+1-_historicTrendConsecutiveDays:index+1] = consecutiveValuesIndexList
                index = index + _historicTrendDayRange + 1
            else:
                index = index + 1
        else:
            consecutiveValuesIndex = 0
            index = index + 1
    return listValuesIndex


def getTrendingDays(df, nTrades, opt, percentChange, nweek, nmonth, nyear):
    def addNone(lst, idx, typeN):
        for i in range(len(lst) - idx):
            result[f'{typeN}Date'].append(None)
            result[f'{typeN}Close'].append(None)
            result[f'{typeN}Percent'].append(None)

    def foundDate(typeN, currDate, currClose, idx, sClose):
        result[f'{typeN}Date'].append(currDate.date())
        result[f'{typeN}Close'].append(currClose)
        pc_week = ((currClose - sClose[idx])/sClose[idx])*100
        result[f'{typeN}Percent'].append(pc_week)

    if nTrades is None or nTrades == 0 or percentChange is None:
        return None

    consecutive_count = 0
    result = {
        'StartDate': [],
        'StartClose': [],
        'EndDate': [],
        'EndClose': [],
        'TotalDays': [],
        'PercentChange': [],
        'WeekDate': [],
        'WeekClose': [],
        'WeekPercent': [],
        'MonthDate': [],
        'MonthClose': [],
        'MonthPercent': [],
        'YearDate': [],
        'YearClose': [],
        'YearPercent': []
    }
    weekList = []
    weekIndex = monthIndex = yearIndex = 0
    monthList = []
    yearList = []
    dateFound = False
    sClose = []
    startDate = startClose = currDate = currClose = 0

    for index, row in df.iterrows():
        if (row['ReturnPercentage'] < percentChange and opt == 'less') or (row['ReturnPercentage'] > percentChange and opt == 'more'):
            consecutive_count += 1
            if consecutive_count == 1:
                startDate = row['Date']
                startClose = row['Close']
        else:
            if consecutive_count >= nTrades:
                row_date = row['Date']
                weekList.append(row_date + relativedelta(weeks=nweek))
                monthList.append(row_date + relativedelta(months=nmonth) - relativedelta(days=1))
                yearList.append(row_date + relativedelta(years=nyear) - relativedelta(days=1))

                sClose.append(row['Close'])
                if dateFound == False:
                    dateFound = True

                result['StartDate'].append(startDate.date())    #type:ignore
                result['StartClose'].append(startClose)
                result['EndDate'].append(row['Date'].date())
                result['EndClose'].append(row['Close'])
                result['TotalDays'].append(consecutive_count)
                pc = ((row['Close'] - startClose)/startClose)*100
                result['PercentChange'].append(pc)

            consecutive_count = 0

        if (dateFound):
            if weekIndex < len(weekList) and row['Date'] > weekList[weekIndex]:
                foundDate('Week', currDate, currClose, weekIndex, sClose)
                weekIndex += 1

            if monthIndex < len(monthList) and row['Date'] > monthList[monthIndex]:
                foundDate('Month', currDate, currClose, monthIndex, sClose)
                monthIndex += 1

            if yearIndex < len(yearList) and row['Date'] > yearList[yearIndex]:
                foundDate('Year', currDate, currClose, yearIndex, sClose)
                yearIndex += 1

            # Update Current Date and Close
            currDate = row['Date']
            currClose = row['Close']

            # Append None values when no more dates in one_weekList
            if df.index.max() == index:
                addNone(weekList, weekIndex, 'Week')
                addNone(monthList, monthIndex, 'Month')
                addNone(yearList, yearIndex, 'Year')

    finaldf = pd.DataFrame.from_dict(result)
    finaldf[['PercentChange', 'WeekPercent', 'MonthPercent', 'YearPercent']] = finaldf[['PercentChange', 'WeekPercent', 'MonthPercent', 'YearPercent']].round(2)

    return finaldf


def generatePerformanceTable(df, monthonmonth_entrytype, monthonmonth_exittype, monthonmonth_tradetype, monthonmonth_entryday, monthonmonth_exitday, monthonmonth_returntype):

    df = df[(df['Weekday'] == monthonmonth_entryday) | (df['Weekday'] == monthonmonth_exitday)][['Date', 'Open', 'Close', 'Weekday']]

    if monthonmonth_entryday == monthonmonth_exitday:
        return None
    
    # Checking for Day Order
    dayOrder = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5}
    startDay = dayOrder[monthonmonth_entryday]
    endDay = dayOrder[monthonmonth_exitday]
    diff = (endDay - startDay) if endDay > startDay else (7 - startDay + endDay)

    df['DaytoDayRP'] = ((df[monthonmonth_exittype].shift(-1) - df[monthonmonth_entrytype]))

    # Filtering Long/Short and Percent/Points
    if monthonmonth_returntype == 'Percent':
        df['DaytoDayRP'] = (df['DaytoDayRP'] / df[monthonmonth_entrytype]) * 100

    if monthonmonth_tradetype == 'Short':
        df['DaytoDayRP'] *= -1

    # Mask to get our Entry Day
    is_day = df['Weekday'] == monthonmonth_entryday

    df['NextDate'] = df['Date'].shift(-1)
    df['DateDifference'] = (df['NextDate'] - df['Date']).dt.days
    

    df = df[(is_day & (df['DateDifference'] == diff))]
    
    if len(df) == 0:
        return None
    
    # Calculating Month on Month Returns
    monthly_sum = df.groupby([df['Date'].dt.year.rename('Year'), df['Date'].dt.strftime('%b').rename('Month')])['DaytoDayRP'].sum().reset_index()

    # Creating a PIVOT TABLE
    pivot_df = monthly_sum.pivot(index='Year', columns='Month', values='DaytoDayRP')
    pivot_df['Total'] = pivot_df.sum(axis=1)
    pivot_df.reset_index(inplace=True)

    # Create a dictionary to assign numerical values to months
    month_to_num = {month: i for i, month in enumerate(monthNames)}

    # Sort the pivot_df.columns list based on the numerical values
    present_months = sorted(pivot_df.columns, key=lambda col: month_to_num.get(col, len(monthNames)))

    pivot_df = pivot_df[['Year'] + present_months].round(2)
    pivot_df = pivot_df.T.drop_duplicates().T
    return pivot_df


def filterDataFrameFromHelper(symbolNameToPlotValue, chartScaleValue,
                              startDate, endDate, dateLastNDaysValue,
                              positiveNegativeYearFilter, evenOddYearFilter, decadeYearsValue,
                              positiveNegativeMonthFilter, evenOddMonthFilter, specificMonthSelectionValue,
                              positiveNegativeExpiryWeekFilter, evenOddExpiryWeekMonthlyFilter,
                              specificExpiryWeekMonthlySelectionValue, evenOddExpiryWeekYearlyFilter,
                              positiveNegativeMondayWeekFilter, evenOddMondayWeekMonthlyFilter,
                              specificMondayWeekMonthlySelectionValue, evenOddMondayWeekYearlyFilter,
                              positiveNegativeDayFilter, weekdayNameFilter,
                              evenOddCalenderMonthDayFilter, evenOddCalenderYearDayFilter,
                              evenOddTradingMonthDayFilter, evenOddTradingYearDayFilter,
                              dailyPercentageChangeFilter, dailyPercentageChangeFilterSwitch,
                              mondayWeeklyPercentageChangeFilter, mondayWeeklyPercentageChangeFilterSwitch,
                              expiryWeeklyPercentageChangeFilter, expiryWeeklyPercentageChangeFilterSwitch,
                              monthlyPercentageChangeFilter, monthlyPercentageChangeFilterSwitch,
                              yearlyPercentageChangeFilter, yearlyPercentageChangeFilterSwitch):

    df = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/1_Daily.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['ExpiryWeeklyDate'] = pd.to_datetime(df['ExpiryWeeklyDate'], format='%Y-%m-%d')
    df['MondayWeeklyDate'] = pd.to_datetime(df['MondayWeeklyDate'], format='%Y-%m-%d')
    df = df.dropna()

    # choose date range
    dateLastNDaysValue = dateLastNDaysValue if (type(dateLastNDaysValue) == int) else 0
    if (dateLastNDaysValue == 0):
        df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)]
    else:
        df = df.tail(dateLastNDaysValue)

    # choose positive/negative, even/odd years
    if (positiveNegativeYearFilter != 'All'):
        df = df[df['PositiveYear'] == positiveNegativeYearFilter]
    if (evenOddYearFilter != 'All'):
        if(evenOddYearFilter != 2):
            df = df[df['EvenYear'] == evenOddYearFilter]
        else:
            df = df[(df['Date'].dt.year % 4 == 0) & ((df['Date'].dt.year % 100 != 0) | (df['Date'].dt.year % 400 == 0))]

    # filter decade years
    decadeYearsValueNotPresent = [x for x in range(1, 11) if x not in decadeYearsValue]
    for decadeYearNotPresent in decadeYearsValueNotPresent:
        if (decadeYearNotPresent == 10):
            decadeYearNotPresent = 0
        df = df[(df['Date'].dt.year % 10) != decadeYearNotPresent]

        # choose positive/negative, even/odd months
    if (positiveNegativeMonthFilter != 'All'):
        df = df[df['PositiveMonth'] == positiveNegativeMonthFilter]
    if (evenOddMonthFilter != 'All'):
        df = df[df['EvenMonth'] == evenOddMonthFilter]
    if (specificMonthSelectionValue != 0):
        df = df[df['Date'].dt.month == specificMonthSelectionValue]

    # choose positive/negative, even/odd expiry weeks
    if (positiveNegativeExpiryWeekFilter != 'All'):
        df = df[df['PositiveExpiryWeek'] == positiveNegativeExpiryWeekFilter]
    if (evenOddExpiryWeekMonthlyFilter != 'All'):
        df = df[df['EvenExpiryWeekNumberMonthly'] == evenOddExpiryWeekMonthlyFilter]
    if ((specificExpiryWeekMonthlySelectionValue != 0) and (specificMonthSelectionValue != 0)):
        df = df[
            (df['ExpiryWeekNumberMonthly'] == specificExpiryWeekMonthlySelectionValue) &
            (df['ExpiryWeeklyDate'].dt.month == specificMonthSelectionValue)
        ]
    elif (specificExpiryWeekMonthlySelectionValue != 0):
        df = df[df['ExpiryWeekNumberMonthly'] == specificExpiryWeekMonthlySelectionValue]
    if (evenOddExpiryWeekYearlyFilter != 'All'):
        df = df[df['EvenExpiryWeekNumberYearly'] == evenOddExpiryWeekYearlyFilter]

    # choose positive/negative, even/odd monday weeks
    if (positiveNegativeMondayWeekFilter != 'All'):
        df = df[df['PositiveMondayWeek'] == positiveNegativeMondayWeekFilter]
    if (evenOddMondayWeekMonthlyFilter != 'All'):
        df = df[df['EvenMondayWeekNumberMonthly'] == evenOddMondayWeekMonthlyFilter]
    if ((specificMondayWeekMonthlySelectionValue != 0) and (specificMonthSelectionValue != 0)):
        df = df[
            (df['MondayWeekNumberMonthly'] == specificMondayWeekMonthlySelectionValue) &
            (df['MondayWeeklyDate'].dt.month == specificMonthSelectionValue)
        ]
    elif (specificMondayWeekMonthlySelectionValue != 0):
        df = df[df['MondayWeekNumberMonthly'] == specificMondayWeekMonthlySelectionValue]
    if (evenOddMondayWeekYearlyFilter != 'All'):
        df = df[df['EvenMondayWeekNumberYearly'] == evenOddMondayWeekYearlyFilter]

    # choose positive/negative, even/odd days
    if (positiveNegativeDayFilter != 'All'):
        df = df[df['PositiveDay'] == positiveNegativeDayFilter]
    if (len(weekdayNameFilter) > 0):
        df = df[df['Weekday'].isin(weekdayNameFilter)]
    if (evenOddCalenderMonthDayFilter != 'All'):
        df = df[df['EvenCalenderMonthDay'] == evenOddCalenderMonthDayFilter]
    if (evenOddCalenderYearDayFilter != 'All'):
        df = df[df['EvenCalenderYearDay'] == evenOddCalenderYearDayFilter]
    if (evenOddTradingMonthDayFilter != 'All'):
        df = df[df['EvenTradingMonthDay'] == evenOddTradingMonthDayFilter]
    if (evenOddTradingYearDayFilter != 'All'):
        df = df[df['EvenTradingYearDay'] == evenOddTradingYearDayFilter]

    # add more columns in dataframe
    df['Year'] = df['Date'].dt.year

    # outlier filters
    if (dailyPercentageChangeFilterSwitch):
        df = df[
            (df['ReturnPercentage'] >= dailyPercentageChangeFilter[0]) &
            (df['ReturnPercentage'] <= dailyPercentageChangeFilter[1])
        ]
    if (mondayWeeklyPercentageChangeFilterSwitch):
        df = df[
            (df['MondayWeeklyReturnPercentage'] >= mondayWeeklyPercentageChangeFilter[0]) &
            (df['MondayWeeklyReturnPercentage'] <= mondayWeeklyPercentageChangeFilter[1])
        ]
    if (expiryWeeklyPercentageChangeFilterSwitch):
        df = df[
            (df['ExpiryWeeklyReturnPercentage'] >= expiryWeeklyPercentageChangeFilter[0]) &
            (df['ExpiryWeeklyReturnPercentage'] <= expiryWeeklyPercentageChangeFilter[1])
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
    return df


def getRecentDayReturnPercentage(df, recentDayValue):
    dayReturnData = pd.DataFrame()
    startValue = 1
    endValue = 1
    dayReturnValue = 0

    try:
        dayReturnData = df.tail(recentDayValue + 1).reset_index(drop=True)
    except:
        print(f"Error in fetching data on {recentDayValue} recent day basis")

    if (len(dayReturnData) > 1):
        startValue = dayReturnData.at[0, 'Close']
        endValue = dayReturnData.at[len(dayReturnData)-1, 'Close']
        dayReturnValue = round(100 * ((endValue - startValue)/startValue), 2)
    else:
        print("Error encountered in calculating Day Return")

    return dayReturnValue


def getRecentWeekReturnPercentage(df, recentWeekValue):
    weekReturnValue = 0
    weekReturnData = pd.DataFrame()
    startValue = 1
    endValue = 1

    try:
        week_start = df['MondayWeeklyDate'].unique()[-recentWeekValue]
        weekReturnData = pd.concat([
            df[df['MondayWeeklyDate'] < week_start].tail(1),
            df[df['MondayWeeklyDate'] >= week_start]
        ]).sort_values(by='Date').reset_index(drop=True)
    except:
        print(f"Error in fetching data on {recentWeekValue} recent week basis")

    if (len(weekReturnData) > 1):
        startValue = weekReturnData.loc[0]['Close']
        endValue = weekReturnData.loc[len(weekReturnData)-1]['Close']
        weekReturnValue = round(100*((endValue - startValue)/startValue), 2)

    else:
        print("Error encountered in calculating weekly return")

    return weekReturnValue


def getRecentMonthReturnPercentage(df, recentmonthValue):
    monthReturnValue = 0
    monthReturnData1 = pd.DataFrame()
    date_end = max(df['Date'])
    yearValue = date_end.year
    monthValue = date_end.month

    if (date_end.month >= recentmonthValue):
        yearValue = date_end.year
        monthValue = date_end.month - (recentmonthValue - 1)
    else:
        yearValue = date_end.year - 1
        monthValue = 12 - (recentmonthValue - date_end.month - 1)

    date_start = pd.to_datetime(date(yearValue, monthValue, 1), format='%Y-%m-%d')

    try:
        monthReturnData1 = pd.concat([
            df[df['Date'] < date_start].tail(1),
            df[df['Date'] >= date_start],
        ]).sort_values(by='Date').reset_index(drop=True)
    except:
        print(f"Error fetching data on {recentmonthValue} recent month basis")

    if (len(monthReturnData1) > 1):
        startValue = monthReturnData1.loc[0]['Close']
        endValue = monthReturnData1.loc[len(monthReturnData1)-1]['Close']
        monthReturnValue = round(100 * ((endValue - startValue) / startValue), 2)
    else:
        print("Error calculating Monthly Return % Value. Returning 0 as default value")

    return monthReturnValue


def getElectionfilterDataFrame(typeName,ElectionInfoDf,df):
    if typeName == "All Years":
        return df
    elif typeName == "Current Year":
        return df[df['Year'] == df['Year'].max()]
    else:
        temp = ElectionInfoDf[typeName.strip()].dropna()
        lst = temp.astype(int).to_list()
        return df[df['Year'].isin(lst)]

def getWeeklyScenarioDataFrame(weekTypeValue,symbolNameToPlotValue, startDate, endDate, chartScaleValue,
    positiveNegativeYearFilter, evenOddYearFilter,
    positiveNegativeMonthFilter, evenOddMonthFilter, specificMonthSelectionValue,
    positiveNegativeWeekFilter, evenOddWeekMonthlyFilter,
    specificWeekMonthlySelectionValue, evenOddWeekYearlyFilter,
    weeklyPercentageChangeFilter, weeklyPercentageChangeFilterSwitch,
    monthlyPercentageChangeFilter, monthlyPercentageChangeFilterSwitch,
    yearlyPercentageChangeFilter, yearlyPercentageChangeFilterSwitch):

    weekTypeValue = "Expiry" if weekTypeValue == "3_Expiry" else "Monday"
    df = pd.read_csv('./Symbols/' + symbolNameToPlotValue + '/1_Daily.csv')
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
        df = df[df[f'Positive{weekTypeValue}Week'] == positiveNegativeWeekFilter]
    if (evenOddWeekMonthlyFilter != 'All'):
        df = df[df[f'Even{weekTypeValue}WeekNumberMonthly'] == evenOddWeekMonthlyFilter]
    if ((specificWeekMonthlySelectionValue != 0) and (specificMonthSelectionValue != 0)):
        df = df[
            (df[f'{weekTypeValue}WeekNumberMonthly'] == specificWeekMonthlySelectionValue) &
            (df[f'{weekTypeValue}WeeklyDate'].dt.month == specificMonthSelectionValue)
        ]
    elif (specificWeekMonthlySelectionValue != 0):
        df = df[df[f'{weekTypeValue}WeekNumberMonthly'] == specificWeekMonthlySelectionValue]
    if (evenOddWeekYearlyFilter != 'All'):
        df = df[df[f'Even{weekTypeValue}WeekNumberYearly'] == evenOddWeekYearlyFilter]

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
    return df