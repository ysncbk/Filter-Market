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
import requests
import bs4 as bs


#set working directory
os.chdir('C:/Users/yasin/Desktop/python/trading')


def save_dax_tickers():
    resp = requests.get('https://de.wikipedia.org/wiki/DAX')
    soup = bs.BeautifulSoup(resp.text,"lxml")
    table = soup.find('table', {'class': "wikitable sortable"})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[1].text
        tickers.append(ticker)
    return tickers
save_dax_tickers()


def get_yahoo_data():
    tickers = save_dax_tickers()
    if not os.path.exists('dax'):
        os.makedirs('dax')   
    start = dt.datetime(2019, 10, 31)
    end = date.today()-timedelta(days=1)
    for ticker in tickers:    
        if not os.path.exists('dax/{}.csv'.format(ticker)):
            stockname = ticker + ".DE"
            df = web.DataReader(stockname, 'yahoo', start, end)
            if ticker == 'CON':
                df.to_csv('dax/A{}.csv'.format(ticker))#In windiws create a file with the name of CON is not possible
            else:
                df.to_csv('dax/{}.csv'.format(ticker))
        else:
            print('Already have {}'.format(ticker))
get_yahoo_data()


def combine_data():
    main_df = pd.DataFrame()
    tickers=save_dax_tickers()
    item = 'CON'
    replace_item = 'ACON'
    if item in tickers:
        loc = tickers.index(item)
        tickers.remove(item)
        tickers.insert(loc, replace_item)
    for ticker in tickers:
        df = pd.read_csv('dax/{}.csv'.format(ticker))
        df.set_index('Date',inplace = True)
        
        df.rename(columns = {'Adj Close': ticker}, inplace = True)
        df.drop(['Open','High','Low','Close','Volume'],1, inplace= True)
        if main_df.empty:
            main_df=df
        else:
            main_df=main_df.join(df,how='outer')
    #print(main_df.head())
    main_df.to_csv('dax_joined_closes.csv')        

combine_data()

def dax_ma():
    df = pd.read_csv('dax_joined_closes.csv',parse_dates=True,index_col=0)
    df = (df.ffill()+df.bfill())/2
    # Calculating the short-window simple moving average
    ma30 = df.rolling(window=30).mean()
    ma30.tail(20)
    
    tickers=save_dax_tickers()
    item = 'CON'
    replace_item = 'ACON'
    if item in tickers:
        loc = tickers.index(item)
        tickers.remove(item)
        tickers.insert(loc, replace_item)
    price_ma=[]
    for ticker in tickers:
        result = df.iloc[-1:,:][ticker]>ma30.iloc[-1:,:][ticker]
        if result.bool() == True:
            price_ma.append(ticker)
        
    print('The price of those stocks are greater than their MA(30) based on adjusted closing prices',price_ma)

dax_ma()

