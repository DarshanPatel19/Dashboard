import pandas as pd
from datetime import datetime, timedelta
df = pd.read_csv('./INDIA.csv', parse_dates=['Date', 'Exit Poll Date', 'StartDate', 'EndDate'], date_parser=(lambda x: pd.to_datetime(x, format='%d-%m-%Y')))
df['PreElectionYears'] = pd.to_datetime(df['PreElectionYears'], format='%Y').dt.strftime('%Y') 
df['PostElectionYears'] = pd.to_datetime(df['PostElectionYears'], format='%Y').dt.strftime('%Y') 
df['MidElectionYears'] = pd.to_datetime(df['MidElectionYears'], format='%Y').dt.strftime('%Y') 
df['Year'] = pd.to_datetime(df['Year'], format='%Y').dt.strftime('%Y') 
df.to_csv('./INDIA.csv', index=False)