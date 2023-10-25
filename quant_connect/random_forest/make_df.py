#region imports
from AlgorithmImports import *
import pandas as pd
from talib import RSI, MACD, NATR, ATR, PPO 
#endregion

def make_df(history_df, intervals):
    ret_df = history_df
    ret_df = add_returns(history_df, intervals)
    ret_df = add_alpha_signals(ret_df) 
    return ret_df

def add_returns(df, intervals):
    ''' Adds returns for time periods specified in intervals'''
    # add lookback returns
    returns = []
    by_symbol = df.groupby('symbol', group_keys=False)
    for t in intervals:
        returns.append(by_symbol.close.pct_change(t).to_frame(f'ret_{t}'))
    returns = pd.concat(returns, axis=1)
    df = pd.merge(df, returns, on=('symbol', 'time'))

    # add forwards returns
    forwards = []
    by_symbol = df.groupby('symbol', group_keys=False)
    for t in intervals:
        label = f'fwd_ret_{t}'
        forwards.append(label)
        df[label] = by_symbol[f'ret_{t}'].shift(-t)
    return df

def add_alpha_signals(df):
    ''' Adds alpha signals to dataframe''' 
    by_symbol = df.groupby('symbol', group_keys=False)
    df['rsi'] = by_symbol.close.apply(RSI)
    df['ppo'] = by_symbol.close.apply(PPO)
    df['atr'] = by_symbol.apply(compute_atr)
    df['macd'] = by_symbol.close.apply(compute_macd) 
    df['natr'] = by_symbol.apply(lambda x: NATR(high=x.high, low=x.low, close=x.close))
    return df 

def compute_atr(stock_data):
    atr = ATR(stock_data.high, stock_data.low, stock_data.close, timeperiod=14)
    return atr.sub(atr.mean()).div(atr.std())

def compute_macd(close):
    macd = MACD(close)[0]
    return macd.sub(macd.mean()).div(macd.std())









