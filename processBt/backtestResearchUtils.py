import json
from typing import List

import pandas as pd
import plotly.express as px
from IPython.display import HTML, display
from QuantConnect import Symbol, SecurityType, Market
from QuantConnect.Packets import BacktestResult
from pandas import DataFrame
from plotly.subplots import make_subplots
import plotly.graph_objects as go

class BTResults:
    ordersDf = pd.DataFrame()
    
    def __init__(self, path):
        self.btData = self.loadData(path)
        self.ordersDf = self.createOrdersDF()

    def loadData(self, path):
        data: BacktestResult = None
        with open(path) as file:
            data = json.load(file)
            return data

    def createOrdersDF(self) -> DataFrame:
        ordersDf = pd.DataFrame.from_records(self.btData['Orders'])
        ordersDf = ordersDf.T
        return ordersDf

    def createOrdersSymbols(self):
        symbols: List[Symbol] = []
        tickers: List[str] = []
        for index, row in self.ordersDf.iterrows():
            symbol: Symbol = Symbol.Create(row['Symbol']['Value'], SecurityType.Equity, Market.USA)
            if symbol.Value not in tickers:
                symbols.append(symbol)
                tickers.append(symbol.Value)
        return symbols

    def getOrdersForSymbol(self, ticker: str) -> DataFrame:
        tickerDf: DataFrame = self.ordersDf.loc[self.ordersDf['Symbol'].str.get('Value') == ticker]
        return tickerDf

    # https://stackoverflow.com/questions/38231591/split-explode-a-column-of-dictionaries-into-separate-columns-with-pandas/63311361#63311361
    def createRollingTradeStats(self):
        rollingWindows = pd.DataFrame.from_records(self.btData['RollingWindow']).T
        # display(rollingWindows[['TradeStatistics']])
        newDf = pd.json_normalize(rollingWindows['TradeStatistics'])
        newDf.index = rollingWindows.index
        # newDf.index = newDf.index
        newDf.index = newDf.index.str.split("_").str[1]
        newDf.set_index(pd.DatetimeIndex(newDf.index), inplace=True)
        return newDf

    def createRollingPortfolioStats(self):
        rollingWindows = pd.DataFrame.from_records(self.btData['RollingWindow']).T
        # display(rollingWindows[['TradeStatistics']])
        newDf = pd.json_normalize(rollingWindows['PortfolioStatistics'])
        newDf.index = rollingWindows.index
        # newDf.index = newDf.index
        newDf.index = newDf.index.str.split("_").str[1]
        newDf.set_index(pd.DatetimeIndex(newDf.index), inplace=True)
        return newDf


def displayStats(df: DataFrame):
    columns = df.columns
    for column in columns[:5]:
        if column not in ['StartDateTime', 'EndDateTime', 'MaximumDrawdownDuration']:
            fig = px.line(df, x=df.index, y=column, labels={'index': "Date"}, title=column)
            fig.show()

#def displayDrawdown(data):
#    drawdownSeries = data["Charts"]["Drawdown"]["Series"]["Equity Drawdown"]["Values"]
# https://www.quantconnect.com/docs/v2/our-platform/api-reference/backtest-management/read-backtest/backtest-statistics
# then search for BacktestResult
# TODO theres three other charts included for algos that use the "framework" model
#  https://www.quantconnect.com/docs/v2/our-platform/backtesting/results
def displayAll(data):
    if "Strategy Equity" in data["Charts"] and "Benchmark" in data["Charts"]:
        displaySeries(data["Charts"]["Strategy Equity"]["Series"]["Equity"], "Strategy Equity")
        displaySeries(data["Charts"]["Strategy Equity"]["Series"]["Daily Performance"], "Strategy Equity")

        displaySeries(data["Charts"]["Benchmark"]["Series"]["Benchmark"], "")
        displaySeries(data["Charts"]["Drawdown"]["Series"]["Equity Drawdown"], "")
        displaySeries(data["Charts"]["Exposure"]["Series"]["Equity - Long Ratio"], "Exposure-")
        displaySeries(data["Charts"]["Exposure"]["Series"]["Equity - Short Ratio"], "Exposure-")
        displaySeries(data["Charts"]["Capacity"]["Series"]["Strategy Capacity"], "")


def displayAssetSalesVolumes(data):
    displayDict(data["Charts"]["Assets Sales Volume"]["Series"], "Asset Sales Volume")

def displayDict(seriesDict: dict, titleSuffix):
    for assetName in seriesDict.keys():
        displaySeries(seriesDict[assetName], titleSuffix)


def displayTable(tableData):
    df = pd.DataFrame.from_records(tableData)
    df = df.T
    return HTML(df.to_html())

def displayScalar(scalarData):
    df = pd.DataFrame.from_records(scalarData, index=[0])
    df = df.T
    return HTML(df.to_html())


def displaySeries(series, titleSuffix):

    #print("IN displaySeries function")
    values = series["Values"]
    #print("values is" + str(values))
    unit = series["Unit"]
    name = series["Name"]
    yLabel = name+ " " + unit
    xLabel = "Date"

    # this has an integer index 0,1,2 , Then "x" as the second column and "y" as the third
    # for example 6,1412654400,0.00
    df = pd.DataFrame(values)
    # display(HTML(df_drawdown.to_html()))

    # this removes the integer index and sets it to the "x" column value (the time in seconds)
    df = pd.DataFrame(df).set_index('x')
    # display(HTML(df_drawdown.to_html()))

    # converts index column to datetime
    df = df.set_index(pd.to_datetime(df.index, unit='s'))
    #print(" convert date to datetime")
    # display(HTML(drawdown.to_html()))

    # adds the index back. why was it removed just to convert "x" to datetime?
    df = df.reset_index()
    #print(" after reset index")
    #display(HTML(df.to_html()))

    #print("done " + name)
    fig = px.line(df, x='x', y='y', labels={'x': xLabel, 'y': yLabel}, title=name+ " "+titleSuffix)  # df.columns)
    #print(" df columns ------")
    #print(df.columns)

    #for col in df.columns:
    #    print(col)

    fig.show()




#def displayTradeStats():

