from QuantConnect.Algorithm import QCAlgorithm
from crossoverAlgo.exits import Exit
from crossoverAlgo.crossoverSetups import Signal
from crossoverAlgo.securityState import SecurityState


class MaxDrawdownExit(Exit):
    def __init__(self, chartState: SecurityState, main: QCAlgorithm):
        super().__init__(chartState, main)
        self.stopMaxDrawdownDollar = 5000
        self.highestUnrealizedProfitDollar = None
        self.stopMaxDrawdownPercent = abs(0.25)
        self.highestUnrealizedProfitPercent = None

    def liquidateSignal(self) -> Signal:
        return self.dollarLiquidateSignal()

    #https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Risk/TrailingStopRiskManagementModel.py
    #https://github.com/IlshatGaripov/Lean/blob/c12868fa3f3c8145a752c86ebd05932adf983359/Algorithm.Framework/Risk/TrailingStopRiskManagementModel.py
    def dollarLiquidateSignal(self)-> Signal:
        result = Signal()

        if not self.main.Portfolio[self.chartState.symbol].Invested:
            result.shouldLiquidate = False
            return result

        profit = self.main.Portfolio[self.chartState.symbol].UnrealizedProfit

        if self.highestUnrealizedProfitDollar == None:
            self.highestUnrealizedProfitDollar = profit if profit > 0 else 0

        # Check for new high and update
        if profit > self.highestUnrealizedProfitDollar:
            self.highestUnrealizedProfitDollar = profit



        # If unrealized profit percent deviates from local max for more than affordable percentage
        if self.highestUnrealizedProfitDollar - self.stopMaxDrawdownDollar > profit :
            result.shouldLiquidate = True
            result.reason = "LIQUIDATE:  DRAWDOWN DOLLAR = " +str(profit) +" <= " \
                            + str(self.highestUnrealizedProfitDollar) + " - " + str(self.stopMaxDrawdownDollar)
        else:
            result.shouldLiquidate = False

        return result

    def percentLiquidateSignal(self)-> Signal:
        result = Signal()

        if not self.main.Portfolio[self.chartState.symbol].Invested:
            result.shouldLiquidate = False
            return result

        profit = self.main.Portfolio[self.chartState.symbol].UnrealizedProfitPercent

        if self.highestUnrealizedProfitPercent == None:
            self.highestUnrealizedProfitPercent = profit if profit > 0 else 0

        # Check for new high and update
        if profit > self.highestUnrealizedProfitPercent:
            self.highestUnrealizedProfitPercent = profit

        # If unrealized profit percent deviates from local max for more than affordable percentage
        if self.highestUnrealizedProfitPercent - self.stopMaxDrawdownPercent > profit:
            result.shouldLiquidate = True
            result.reason = "LIQUIDATE:  DRAWDOWN PERCENT = " + str(profit) + " <= " \
                            + str(self.highestUnrealizedProfitPercent) + " - " + str(self.stopMaxDrawdownPercent)
        else:
            result.shouldLiquidate = False

        return result