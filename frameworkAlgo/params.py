from QuantConnect.Algorithm import QCAlgorithm


class Params:
    LTM_SMA_SLOW_PERIOD: int = 0
    LTM_SMA_FAST_PERIOD: int = 0
    RSI_PERIOD: int = 0
    ATR_PERIOD: int = 0
    ADX_PERIOD: int = 0
    RSI_MAX_DAYS: int =0
    RSI_PERCENT_PROFIT: float = 0
    RSI_STOP_LOSS_MULTIPLIER: int = 0
    LTM_STOP_LOSS_MULTIPLIER: int = 0
    LTM_TRAILING_STOP_PERCENT: float = 0
    LTM_BENCH_SMA: int = 0
    POSITION_PERCENT: float = 0
    CROSSOVER_TOLERANCE: float = 0
    LTM_SHORTS: bool = False
    LTM_LONGS: bool = True
    ADX_RSI_UNIVERSE_PERIOD: int = 0
    ATR_RSI_UNIVERSE_PERIOD: int = 0
    RSI_LONG_INDICATOR: int = 0
    RSI_SHORT_INDICATOR: int = 0

    @classmethod
    def setup(cls, main: QCAlgorithm):
        cls.LTM_SMA_FAST_PERIOD = main.GetParameter("sma-fast", 100)
        cls.LTM_SMA_SLOW_PERIOD = main.GetParameter("sma-slow", 200)
        cls.RSI_PERIOD = main.GetParameter("rsi", 3)
        cls.RSI_LONG_INDICATOR = main.GetParameter("rsi-long", 20)
        cls.RSI_SHORT_INDICATOR = main.GetParameter("rsi-short", 90)
        cls.ATR_PERIOD = main.GetParameter("atr", 20)
        cls.ADX_PERIOD = main.GetParameter("adx", 10)
        cls.ADX_RSI_UNIVERSE_PERIOD = main.GetParameter("adx-rsi-universe", 7)
        cls.ATR_RSI_UNIVERSE_PERIOD = main.GetParameter("atr-rsi-universe", 10)
        cls.RSI_MAX_DAYS = main.GetParameter("rsi-max-days", 5)
        cls.RSI_PERCENT_PROFIT = main.GetParameter("rsi-percent-profit", .06)
        cls.RSI_STOP_LOSS_MULTIPLIER = main.GetParameter("rsi-stop-multiplier", 5)
        cls.LTM_STOP_LOSS_MULTIPLIER = main.GetParameter("ltm-stop-multiplier", 5)
        cls.LTM_TRAILING_STOP_PERCENT= main.GetParameter("ltm-trailing-stop-percent", .15)
        cls.LTM_BENCH_SMA= main.GetParameter("ltm-bench-sma", 100)
        cls.POSITION_PERCENT= main.GetParameter("position-percent", .4)
        cls.UNIVERSE_ROC_PERIOD= main.GetParameter("roc-period", 200)
        cls.CROSSOVER_TOLERANCE= main.GetParameter("crossover-tolerance", .05)



