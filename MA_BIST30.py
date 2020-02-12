# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 07:36:32 2020

@author: yasin
"""

# import libraries
import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime as dt
from datetime import date, timedelta
import pandas_datareader.data as web
import pandas as pd
import os
import numpy as np
#set working directory
os.chdir('C:/Users/yasin/Desktop/python/trading')


def x30_tickers():    
    url = "http://finans.mynet.com/borsa/endeks/xu030-bist-30/endekshisseleri/"
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    table=soup.find_all('table')
    x30 = []
    for row in table[0].find_all('tr'):
        for stock in row.find_all('a'):
            x30.append(stock.text[0:5].strip())
    return x30
#x30_tickers()

def get_yahoo_data(reload_x30= False):
    tickers = x30_tickers()
    if not os.path.exists('x30'):
        os.makedirs('x30')   
    start = dt.datetime(2019, 10, 31)
    end = date.today()
    for ticker in tickers:#[:5]
        if not os.path.exists('x30/{}.csv'.format(ticker)):
            stockname = ticker + ".IS"
            df = web.DataReader(stockname, 'yahoo', start, end)
            df.to_csv('x30/{}.csv'.format(ticker))
        else:
            print('Already have {}'.format(ticker))

get_yahoo_data()

def combine_data():
    main_df = pd.DataFrame()
    tickers=x30_tickers()
    for ticker in tickers:
        df = pd.read_csv('x30/{}.csv'.format(ticker))
        df.set_index('Date',inplace = True)
        
        df.rename(columns = {'Adj Close': ticker}, inplace = True)
        df.drop(['Open','High','Low','Close','Volume'],1, inplace= True)
        if main_df.empty:
            main_df=df
        else:
            main_df=main_df.join(df,how='outer')
    #print(main_df.head())
    main_df.to_csv('xu030_joined_closes.csv')        

combine_data()

def x30_ma():
    df = pd.read_csv('xu030_joined_closes.csv',parse_dates=True,index_col=0)
    df = (df.ffill()+df.bfill())/2
    # Calculating the short-window simple moving average
    ma30 = df.rolling(window=30).mean()
    ma30.tail(20)
    
    tickers=x30_tickers()
    price_ma=[]
    for ticker in tickers:
        result = df.iloc[-1:,:][ticker]>ma30.iloc[-1:,:][ticker]
        if result.bool() == True:
            price_ma.append(ticker)
        
    print('The price of those stocks are greater than their MA(30) based on adjusted closing prices',price_ma)

x30_ma()

