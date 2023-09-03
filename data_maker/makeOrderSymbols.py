import json
from typing import List

import pandas as pd
from pandas import DataFrame


class BtParser:
    ordersDf = pd.DataFrame()

    def __init__(self, path):
        self.btData = self.loadData(path)
        self.ordersDf = self.createOrdersDF()

    def loadData(self, path):
        data: {} = None
        with open(path) as file:
            data = json.load(file)
            return data

    def createOrdersDF(self) -> DataFrame:
        ordersDf = pd.DataFrame.from_records(self.btData['Orders'])
        ordersDf = ordersDf.T
        return ordersDf

    def createOrdersSymbols(self):
        tickers: List[str] = []
        for index, row in self.ordersDf.iterrows():
            value: str = row['Symbol']['Value']
            if value not in tickers:
                tickers.append(value)
        return tickers



def makeOrderSymbols():
    btRes = BtParser("backtests/2022-10-31_19-36-26/1222378425.json")
    btData = btRes.btData
    symbols = btRes.createOrdersSymbols()
    print(symbols)

makeOrderSymbols()