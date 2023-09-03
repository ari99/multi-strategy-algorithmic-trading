from datetime import timedelta, datetime

from QuantConnect import Symbol, Resolution
from QuantConnect.Research import QuantBook
from pandas import DataFrame
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta

'''    #symbolAdded = qb.AddEquity("SPY").Symbol
    #subset_history_df = qb.History([spy, tlt], start_time, end_time)
    #all_history_df = qb.History(qb.Securities.Keys, start_time, end_time)
    #history = qb.History(symbol, timedelta(days=30), Resolution.Daily)
    '''
class EquityChart:

    def createHistory(self, qb: QuantBook, symbolAdded: Symbol ):
        start_time = datetime(2014, 1, 1)
        end_time = datetime(2022, 12, 8)
        history = qb.History(symbolAdded, start_time, end_time, Resolution.Daily)
        data = history.loc[symbolAdded]
        data = data.reset_index()
        data.set_index(pd.DatetimeIndex(data["time"]), inplace=True)
        return data

    def addIndicators(self, historyDf: DataFrame):
        historyDf.ta.log_return(cumulative=True, append=True)
        historyDf.ta.sma(length=10, append=True)
        historyDf.ta.sma(length=50, append=True)
        historyDf.ta.macd(append=True)
        historyDf.ta.cdl_pattern(name="doji", append=True)
        return historyDf

    def displayEquityChart(self, symbol: Symbol, historyDf: DataFrame):

        fig = make_subplots(rows=2,
                            cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.25,
                            subplot_titles=(f"{symbol} OHLC", 'Volume'),
                            row_heights=[0.7, 0.2])

        trace1 = go.Candlestick(x=historyDf.index,
                                open=historyDf['open'],
                                high=historyDf['high'],
                                low=historyDf['low'],
                                close=historyDf['close'],
                                name='Price')
        #print(historyDf)
        trace2 = go.Scatter(x=historyDf.index, y=historyDf['SMA_10'],
                            mode='lines',
                            name='SMA_10')
        # trace2.up
        fig.add_trace(trace1, row=1, col=1)
        fig.add_trace(trace2, row=1, col=1)

        fig.add_trace(go.Bar(x=historyDf.index, y=historyDf['volume'], showlegend=False, name="Volume"), row=2, col=1)
        fig['layout'].update(height=1000, width=1000, title=symbol.Value)
        fig.update(layout_xaxis_rangeslider_visible=True)
        fig.update_yaxes(fixedrange=False)

        fig.show()
