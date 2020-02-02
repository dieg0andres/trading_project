import sqlite3
import pandas as pd
import technical_indicators as ti
import performance_indicators as pi
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas_datareader.data as pdr


#db_funcs.update_sp500co_daily_table()


'''


conn =sqlite3.connect('trading_database.db')
cur = conn.cursor()
ticker = '^GSPC'
cur.execute("SELECT date, high, low, adj_close, volume, open from sp500co_daily WHERE symbol = ?", (ticker,))
data = cur.fetchall()
conn.close()

date = [c[0] for c in data]
high = [c[1] for c in data]
low= [c[2] for c in data]
adj_close = [c[3] for c in data]
volume = [int(c[4]) for c in data]
open = [c[5] for c in data]



sp500 = pd.DataFrame({'date': date, 'high': high, 'low': low, 'adj_close': adj_close, 'volume':volume, 'open': open})
sp500.set_index('date', inplace=True)


sp_ret = pi.CAGR(sp500[-252*5:])
sp_vol = pi.volatility(sp500[-252*5:])
sp_shr = pi.sharpe(sp500[-252*5:], 0.022)
sp_mdd = pi.max_draw_down(sp500[-252*5:])
sp_cmr = pi.calmar(sp500[-252*5:])

print(sp_ret, sp_vol, sp_shr, sp_mdd, sp_cmr)

#plt.subplot(2,1,1)
#ADX[-200:].plot()
#plt.subplot(2,1,2)
#sp500['adj_close'][-200:].plot()
#plt.show()
'''


ticker = 'XOM'
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(252)
temp = pdr.get_data_yahoo(ticker, start_date, end_date, interval='y')
pass