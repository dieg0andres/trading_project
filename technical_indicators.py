import copy
import pandas as pd
import statsmodels.api as sm
import numpy as np
from stocktrends import Renko
import datetime


def MACD(df_, fast, slow, sig):
    """implements Moving Average Convergence Divergence
    df_ : a pandas.DataFrame with column 'close'
    fast: the period for fast moving average
    slow: the period for slow moving average
    sig : the period for signal moving average
    typical values are: 12, 26, 9
    returns: a pandas.DataFrame with columns: MACD, signal"""
    df = copy.deepcopy(df_)
    df['MA_fast'] = df['close'].ewm(span=fast, min_periods=fast).mean()
    df['MA_slow'] = df['close'].ewm(span=slow, min_periods=slow).mean()
    df['MACD'] = df['MA_fast'] - df['MA_slow']
    df['signal'] = df['MACD'].ewm(span=sig, min_periods=sig).mean()
    df.dropna(axis=0,inplace=True)
    return df[['MACD', 'signal']]

def ATR(df_, n):
    '''implements Average True Range Technical Indicator
    df_ : a pandas.DataFrame with columns: 'high', 'low', 'adj_close'
    uses regular average not exponential average
    returns a pandas.DataFrame with two columns: 'TR' and 'ATR'
    '''
    df = copy.deepcopy(df_)
    df['H-L'] = df['high'] - df['low']
    df['H-pC']= abs(df['high'] - df['adj_close'].shift(1))
    df['L-pC']= abs(df['low'] - df['adj_close'].shift(1))
    df['TR'] = df[['H-L', 'H-pC', 'L-pC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df.dropna(axis=0, inplace=True)
    return df[['TR', 'ATR']]

def bol_bands(df_, n):
    df = copy.deepcopy(df_)
    df['MA']    = df['adj_close'].rolling(n).mean()
    df['BB_up'] = df['MA'] + 2*df['MA'].rolling(n).std()
    df['BB_dn'] = df['MA'] - 2*df['MA'].rolling(n).std()
    df['BB_width'] = df['BB_up'] - df['BB_dn']
    df.dropna(inplace=True)
    return df

def RSI(df_, n):
    """Relative Strength Index - 30-70"""
    df = copy.deepcopy(df_)
    df['delta'] = df['adj_close'] - df['adj_close'].shift(1)
    df['gain'] = np.where(df['delta'] >= 0, df['delta'], 0)
    df['loss'] = np.where(df['delta'] <  0, abs(df['delta']), 0)
    avg_gain = []
    avg_loss = []
    gain = df['gain'].tolist()
    loss = df['loss'].tolist()

    for i in range(df.shape[0]):
        if i < n:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == n:
            avg_gain.append(df['gain'].rolling(n).mean().tolist()[n])
            avg_loss.append(df['loss'].rolling(n).mean().tolist()[n])
        elif i > n:
            avg_gain.append((avg_gain[i-1]*(n-1) + gain[i])/n)
            avg_loss.append((avg_loss[i-1]*(n-1) + loss[i])/n)

    df['avg_gain'] = np.array(avg_gain)
    df['avg_loss'] = np.array(avg_loss)
    df['RS'] = df['avg_gain'] / df['avg_loss']
    df['RSI'] = 100 - (100 / (1 + df['RS']))
    df.dropna(inplace=True)
    return df['RSI']


def ADX(df_, n):
    ''' implements Average Directional Index... n usually 14'''
    df = copy.deepcopy(df_)
    df['H-L'] = df['high'] - df['low']
    df['H-pC'] = abs(df['high'] - df['adj_close'].shift(1))
    df['L-pC'] = abs(df['low'] - df['adj_close'].shift(1))
    df['TR'] = df[['H-L', 'H-pC', 'L-pC']].max(axis=1, skipna=False)
    df['DMplus'] = np.where(df['high']-df['high'].shift(1)>df['low'].shift(1)-df['low'], df['high']-df['high'].shift(1),0)
    df['DMplus'] = np.where(df['DMplus'] < 0, 0, df['DMplus'])
    df['DMminus']= np.where(df['low'].shift(1)-df['low']>df['high']-df['high'].shift(1), df['low'].shift(1)-df['low'],0)
    df['DMminus']= np.where(df['DMminus']<0,0,df['DMminus'])

    TR = df['TR'].tolist()
    DMplus = df['DMplus'].tolist()
    DMminus= df['DMminus'].tolist()

    TRn = []
    DMplusN = []
    DMminusN = []

    for j in range(len(TR)):
        if j < n:
            TRn.append(np.NaN)
            DMplusN.append(np.NaN)
            DMminusN.append(np.NaN)
        elif j == n:
            TRn.append(df['TR'].rolling(n).sum().tolist()[n])
            DMplusN.append(df['DMplus'].rolling(n).sum().tolist()[n])
            DMminusN.append(df['DMminus'].rolling(n).sum().tolist()[n])
        elif j > n:
            TRn.append(TRn[j-1] - (TRn[j-1]/n) + TR[j])
            DMplusN.append(DMplusN[j-1] - (DMplusN[j-1]/n) + DMplus[j])
            DMminusN.append(DMminusN[j-1] - (DMminusN[j-1]/n) + DMminus[j])

    df['TRn'] = np.array(TRn)
    df['DMplusN'] = np.array(DMplusN)
    df['DMminusN']= np.array(DMminusN)

    df['DIplusN'] = 100 * df['DMplusN'] / df['TRn']
    df['DIminusN']= 100 * df['DMminusN']/ df['TRn']
    df['DIdiff'] = abs(df['DIplusN'] - df['DIminusN'])
    df['DIsum'] = df['DIplusN'] + df['DIminusN']

    df['DX'] = 100 * (df['DIdiff'] / df['DIsum'])

    ADX = []
    DX = df['DX'].tolist()

    for j in range(df.shape[0]):
        if j < 2*n-1:
            ADX.append(np.NaN)
        elif j == 2*n-1:
            ADX.append(df['DX'][j-n+1:j+1].mean())
        elif j > 2*n-1:
            ADX.append(((n-1)*ADX[j-1] + DX[j])/n)

    df['ADX'] = np.array(ADX)
    df.dropna(inplace=True)
    return df['ADX']


def OBV(df_):
    ''' implements on balance volume, leading indicator'''

    df = copy.deepcopy(df_)
    df['daily_ret'] = df['adj_close'].pct_change()
    df['direction'] = np.where(df['daily_ret']>0,1,-1)
    df.at[df.index[0],'direction'] = 0
    df['volxdir'] = df['volume']*df['direction']
    df['obv'] = df['volxdir'].cumsum()
    return df['obv']


def slope(ser, n):
    # function to calculate the slope of n consecutive points on a plot
    # ser needs to be a numpy.array

    slopes = [i*0 for i in range(n-1)]

    for i in range(n, len(ser)+1):
        x = np.array(range(n))
        y = ser[i-n:i]

        x_scaled = (x - x.min())/(x.max() - x.min())
        y_scaled = (y - y.min())/(y.max() - y.min())

        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])

    return np.array(slopes)


def his_slope(ser,n):
    "function to calculate the slope of n consecutive points on a plot"
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    return np.array(slopes)

def renko_DF(df_):
    """ converts ohlc data into renko bricks
    must include the following columns: 'date' 'open' 'high' 'low' 'close'
    """
    df = copy.deepcopy(df_)
    if 'adj_close' in df.columns:
        df['close'] = df['adj_close']

    df.reset_index(inplace=True)
    df2 = Renko(df)
    df2.brick_size = round(ATR(df_, 120)['ATR'][-1],0)

    renko_df = df2.get_ohlc_data()
    return renko_df



