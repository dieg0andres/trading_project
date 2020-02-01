import sqlite3
import data_pulls
from dateutil import parser
import datetime as dt

def create_s_p500_co_table():
    conn = sqlite3.connect('trading_database.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS s_p500_co (
        symbol TEXT PRIMARY KEY,
        security TEXT,
        GCIS_sector TEXT,
        GCIS_sub_industry TEXT,
        CIK TEXT )""")
    conn.commit()
    conn.close()

def populate_s_p500_co_table():
    conn = sqlite3.connect('trading_database.db')
    cur = conn.cursor()

    s_p500co_dict = data_pulls.s_p500_co()

    for i in range(len(s_p500co_dict['symbol'])):
        cur.execute("INSERT INTO s_p500_co VALUES (?,?,?,?,?)",
                  (s_p500co_dict['symbol'][i],
                   s_p500co_dict['security'][i],
                   s_p500co_dict['GCIS_sector'][i],
                   s_p500co_dict['GCIS_sub_industry'][i],
                   s_p500co_dict['CIK'][i],)
                  )
        conn.commit()
    conn.close()

def create_sp500_co_daily_table():
    conn = sqlite3.connect('trading_database.db')
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS sp500co_daily (
        symbol TEXT NOT NULL,
        date DATETIME NOT NULL,
        high REAL,
        low REAL,
        open REAL,
        close REAL,
        volume INTEGER,
        adj_close REAL,
        CONSTRAINT PK_sp500co_daily PRIMARY KEY(symbol, date)
        )""")
    conn.commit()
    conn.close()

def populate_sp500_co_daily_table(start_date = dt.date.today() - dt.timedelta(30 * 365)):
    conn = sqlite3.connect('trading_database.db')
    cur = conn.cursor()

    stocks = data_pulls.sp500co_daily_yahoo(start_date)

    for key in stocks.keys():
        print('entering data: ', key)
        for row in range(stocks[key].shape[0]):
            try:
                cur.execute("INSERT INTO sp500co_daily VALUES (?,?,?,?,?,?,?,?)",
                            (key,
                             parser.parse(str(stocks[key].index[row])[:10]),
                             float("{0:.2f}".format(stocks[key].iat[row, 0])),
                             float("{0:.2f}".format(stocks[key].iat[row, 1])),
                             float("{0:.2f}".format(stocks[key].iat[row, 2])),
                             float("{0:.2f}".format(stocks[key].iat[row, 3])),
                             int(stocks[key].iat[row, 4]),
                             float("{0:.2f}".format(stocks[key].iat[row, 5])))
                            )
            except Exception as e:
                print('error in loading ', key, ' ', parser.parse(str(stocks[key].index[row])[:10]), '\n', e)
                continue

    conn.commit()
    conn.close()

def update_sp500co_daily_table():
    conn = sqlite3.connect('trading_database.db')
    cur = conn.cursor()
    sql = "SELECT date FROM sp500co_daily ORDER BY date DESC LIMIT 1"
    cur.execute(sql)
    temp = cur.fetchall()
    conn.close()

    last_date_entered = parser.parse(temp[0][0][:10])

    if dt.datetime.today() > last_date_entered:
        populate_sp500_co_daily_table(start_date= last_date_entered + dt.timedelta(1))

