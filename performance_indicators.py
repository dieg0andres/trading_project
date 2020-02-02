import copy
import numpy as np


def CAGR(df_):
    ''' df_ must be have daily data'''
    df = copy.deepcopy(df_)
    df['daily_return'] = df['adj_close'].pct_change()
    df['cum_return'] = (1 + df['daily_return']).cumprod()
    n = df.shape[0]/252
    CAGR_ = (df['cum_return'][-1])**(1/n) - 1
    return CAGR_

def volatility(df_):
    ''' df_ must be daily data'''

    df = copy.deepcopy(df_)
    df['daily_return'] = df['adj_close'].pct_change()
    vol = df['daily_return'].std() * np.sqrt(252)
    return vol

def sharpe(df_, rf):
    ''' df_ must be daily data'''
    df = copy.deepcopy(df_)
    s = (CAGR(df) - rf) / volatility(df)
    return s

def max_draw_down(df_):
    df = copy.deepcopy(df_)
    df['daily_return'] = df['adj_close'].pct_change()
    df['cum_return'] = (1 + df['daily_return']).cumprod()
    df['cum_roll_max'] = (df['cum_return']).cummax()
    df['draw_down'] = df['cum_roll_max'] - df['cum_return']
    df['draw_down_pct'] = df['draw_down'] / df['cum_roll_max']
    max_draw_down = df['draw_down_pct'].max()
    return max_draw_down

def calmar(df_):
    df = copy.deepcopy(df_)
    clmr = CAGR(df) / max_draw_down(df)
    return clmr



