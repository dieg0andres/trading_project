import sqlite3
import pandas as pd
import technical_indicators
import matplotlib.pyplot as plt


#db_funcs.update_sp500co_daily_table()




conn =sqlite3.connect('trading_database.db')
cur = conn.cursor()
ticker = '^GSPC'
cur.execute("SELECT date, high, low, adj_close from sp500co_daily WHERE symbol = ?", (ticker,))
data = cur.fetchall()
conn.close()

date = [c[0] for c in data]
high = [c[1] for c in data]
low= [c[2] for c in data]
adj_close = [c[3] for c in data]


sp500 = pd.DataFrame({'date': date, 'high': high, 'low': low, 'adj_close': adj_close})
sp500.set_index('date', inplace=True)



RSI = technical_indicators.RSI(sp500, 20)
his_RSI = technical_indicators.his_RSI(sp500, 20)

#plt.subplot(2,1,1)
#RSI[-200:].plot()
#plt.subplot(2,1,2)
#sp500['adj_close'][-200:].plot()
#plt.show()
pass