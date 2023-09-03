import json
from pathlib import Path
from typing import Dict, List

import jsons
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Algorithm.Framework import Portfolio
from QuantConnect.Data import Slice
from QuantConnect.Data.Market import TradeBar
from QuantConnect.Securities import SecurityHolding


class CombinedStat:
    def __init__(self):
        self.holdingsValue: float = 0
        self.profit: float = 0
        self.unrealizedProfit: float = 0
        self.unrealizedProfitPercent: float = 0


class StatHistory:
    def __init__(self):
        self.holdingsValues: List = []
        self.profits: [] = []
        self.unrealizedProfits: [] = []
        self.unrealizedProfitPercent: List = []


class SecurityStatHistory(StatHistory):
    def __init__(self):
        super().__init__()
        self.ticker: str = ""
        self.averagePrices: [] = []
        self.isLongs: [] = []
        self.isShorts: [] = []
        self.quantitys: [] =[]


class StatsHistory:
    def __init__(self):
        self.totalStats: Dict = {}
        self.allCombinedStats: StatHistory = StatHistory()
        self.securityStats: Dict[str, SecurityStatHistory] = {}

class StatsHistorySerivce:
    def __init__(self, main: QCAlgorithm):
        self.statsHistory = StatsHistory()
        self.main = main

    def setTotalStats(self, param):
        self.statsHistory.totalStats = param

    def appendCombinedStat(self, timestamp: float,  combinedStat: CombinedStat):
        self.statsHistory.allCombinedStats.holdingsValues.append([timestamp, combinedStat.holdingsValue])
        self.statsHistory.allCombinedStats.profits.append([timestamp, combinedStat.profit])
        self.statsHistory.allCombinedStats.unrealizedProfits.append([timestamp, combinedStat.unrealizedProfit])
        self.statsHistory.allCombinedStats.unrealizedProfitPercent.append([timestamp, combinedStat.unrealizedProfitPercent])

    def appendSecurityStat(self, timestamp: float,  holding: SecurityHolding ):
        ticker: str = holding.Symbol.Value
        if ticker not in self.statsHistory.securityStats:
            self.statsHistory.securityStats[ticker] = SecurityStatHistory()
            self.statsHistory.securityStats[ticker].ticker = ticker
        else:
            self.statsHistory.securityStats[ticker].profits.append([timestamp, holding.Profit])
            self.statsHistory.securityStats[ticker].holdingsValues.append([timestamp, holding.HoldingsValue])
            self.statsHistory.securityStats[ticker].unrealizedProfits.append([timestamp, holding.UnrealizedProfit])
            self.statsHistory.securityStats[ticker].unrealizedProfitPercent.append([timestamp, holding.UnrealizedProfitPercent])
            self.statsHistory.securityStats[ticker].averagePrices.append([timestamp, holding.AveragePrice])
            self.statsHistory.securityStats[ticker].quantitys.append([timestamp, holding.Quantity])
            self.statsHistory.securityStats[ticker].isLongs.append([timestamp, holding.IsLong])
            self.statsHistory.securityStats[ticker].isShorts.append([timestamp, holding.IsShort])

    def getStatsHistory(self):
        return self.statsHistory


# https://www.quantconnect.com/forum/discussion/1422/how-can-i-get-current-trade-profits-portfolio-spysymbol-lasttradeprofit/p1
# https://www.quantconnect.com/forum/discussion/7631/how-to-check-holdings-profit-loss-percentage/p1
class StatTracker:
    debugCount = 0
    previousQuantity = 0

    def __init__(self, main: QCAlgorithm):
        self.main = main
        self.statsHistoryService: StatsHistorySerivce = StatsHistorySerivce(main)

    def processSlice(self, slice: Slice):
        combinedStat: CombinedStat = CombinedStat()

        #timestamp: int = (slice.Time).apply(lambda x: int((x.value / 10**6)))
        #timestamp: int = (slice.Time).replace(tzinfo=timezone.utc).timestamp() * 1000
        timestamp: int = int((slice.Time).timestamp() * 1000)
        for symbol, trade_bar in slice.Bars.items():  # there is 1 tradebar for each symbol
            tradeBar: TradeBar = trade_bar
            holding: SecurityHolding = self.main.Portfolio[symbol]

            if str(holding.Symbol) == 'AMZN' and StatTracker.debugCount < 3 \
                    and holding.Quantity > 5 and holding.Quantity != StatTracker.previousQuantity:

                StatTracker.previousQuantity = holding.Quantity
                StatTracker.debugCount += 1

                self.main.Debug(str(StatTracker.previousQuantity) + " " + str(holding.Quantity) + " "
                                + str(holding.Symbol) + " tradeBar EndTime " + str(tradeBar.EndTime)
                    + " tradeBar Time " + str(tradeBar.Time)
                    + " slice Time " + str(slice.Time)
                    + "\n Currently invested: "
                    + "\n\t symbol: " + str(holding.Symbol)
                    + "\n\t quantity: "+ str(holding.Quantity)
                    + "\n\t Profit: " + str(holding.Profit)
                    + "\n\t HoldingsValue: " + str(holding.HoldingsValue)
                    + "\n\t UnrealizedProfit: " + str(holding.UnrealizedProfit)
                    + "\n\t AbsoluteHoldingsValue: " + str(holding.AbsoluteHoldingsValue)
                    + "\n\t TotalSaleVolume: " + str(holding.TotalSaleVolume)
                    + "\n\t AbsoluteHoldingsCost: " + str(holding.AbsoluteHoldingsCost)
                    + "\n\t HoldingsCost: " + str(holding.HoldingsCost)
                    + "\n\t AveragePrice: " + str(holding.AveragePrice)

                    + "\n\t Price: " + str(holding.Price)
                    + "\n\t AbsoluteHoldingsCost: " + str(holding.AbsoluteHoldingsCost)
                    + "\n\t HoldingsCost: " + str(holding.HoldingsCost)
                    + "\n\t AveragePrice: " + str(holding.AveragePrice)
                    + "\n\t QuantityValue: " + str(holding.GetQuantityValue(holding.Quantity))
                            )

            combinedStat.profit += holding.Profit
            combinedStat.holdingsValue += holding.HoldingsValue
            combinedStat.unrealizedProfit += holding.UnrealizedProfit
            combinedStat.unrealizedProfitPercent += holding.UnrealizedProfitPercent

            self.statsHistoryService.appendSecurityStat(timestamp, holding)

        self.statsHistoryService.appendCombinedStat(timestamp, combinedStat)

    def processEndPortfolio(self, portfolio: Portfolio):
        self.statsHistoryService.setTotalStats ( {
            "Cash": portfolio.Cash,
            "TotalPortfolioValue": portfolio.TotalPortfolioValue,
            "TotalUnrealisedProfit": portfolio.TotalUnrealisedProfit,
            "TotalAbsoluteHoldingsCost": portfolio.TotalAbsoluteHoldingsCost,
            "TotalHoldingsValue": portfolio.TotalHoldingsValue,
            "TotalProfit": portfolio.TotalProfit,
        })

    def writeStats(self, path: str):
        jsonVal = jsons.dump(self.statsHistoryService.getStatsHistory())
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as outfile:
            json.dump(jsonVal, outfile, ensure_ascii=False, indent=4)
            self.main.Debug("finished  writing stats to " + path)

