import bs4 as bs
from requests import get
import sqlite3
import datetime as dt
import pandas_datareader.data as pdr

def s_p500_co():
    '''scrapes wikipedia for a list of the S&P500 companies and returns a dict
    '''
    response = get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')

    if response.status_code != 200:
        raise Exception('response from Wikipedia was {}'.format(response.status_code))

    soup = bs.BeautifulSoup(response.text, 'lxml')
    table = soup.find('table')
    rows = table.find_all('tr')

    s_p500_co_dict = {
        'symbol' : [],
        'security' : [],
        'GCIS_sector' : [],
        'GCIS_sub_industry' : [],
        'CIK' : []
    }

    for i, r in enumerate(rows):
        if i != 0:
            s_p500_co_dict['symbol'].append(r.text.split('\n')[1])
            s_p500_co_dict['security'].append(r.text.split('\n')[3])
            s_p500_co_dict['GCIS_sector'].append(r.text.split('\n')[5])
            s_p500_co_dict['GCIS_sub_industry'].append(r.text.split('\n')[6])
            s_p500_co_dict['CIK'].append(r.text.split('\n')[9])

    return s_p500_co_dict


def sp500co_daily_yahoo(start_date):
    conn = sqlite3.connect('trading_database.db')
    cur = conn.cursor()

    cur.execute("SELECT symbol FROM s_p500_co")
    tickers = [t[0] for t in cur.fetchall()]
    tickers.append('^GSPC')

    end_date = dt.date.today()

    stocks = {}
    attempt = 0
    drop = []

    while len(tickers) != 0 and attempt <= 5:
        tickers = [j for j in tickers if j not in drop]
        for i in range(len(tickers)):
            try:
                temp = pdr.get_data_yahoo(tickers[i], start_date, end_date)
                stocks[tickers[i]] = temp
                drop.append(tickers[i])
                print('got data for:', tickers[i])
            except:
                print(tickers[i], ': failed to get data... retrying')
                continue
        attempt += 1

    for key in stocks.keys():
        stocks[key].fillna(method='bfill', axis=0, inplace=True)

    return stocks

