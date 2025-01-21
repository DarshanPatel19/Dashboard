import pandas as pd
import os
import glob
filesList = glob.glob(os.path.join(os.path.curdir, '*.csv'), recursive=True)
for file in filesList:
    if 'Seasonality.csv' in file:
        df = pd.read_csv(file)
        df['Open'].fillna(df['Close'], inplace=True)
        df['High'].fillna(df['Close'], inplace=True)
        df['Low'].fillna(df['Close'], inplace=True)
        df = df.reset_index(drop=True)
        df['Ticker'] = ['SENSEX']*len(df)
        df = df[['Ticker', 'Date', 'Open', 'High', 'Low', 'Close']]
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
        df = df.sort_values(by='Date')
        df['Date'] = df['Date'].dt.strftime('%d-%m-%Y')
        df['Volume'] = [0]*len(df)
        df['OpenInterest'] = [0]*len(df)
        df.to_csv(file, index=False)
        