from enum import Enum

from frameworkAlgo.mainHolder import Main


class SourceKey(Enum):
    RSI_ALPHA: 'SourceKey' = "rsi_alpha"
    RSI_RISK: 'SourceKey' = "rsi_risk"
    RSI_PROFIT_PERCENT: 'SourceKey' = "rsi_profit_percent"
    RSI_MAX_DAYS: 'SourceKey' = "rsi_max_days"
    RSI_STOP: 'SourceKey' = "rsi_stop"
    RSI_END: 'SourceKey' = "rsi_end"
    LTM_ALPHA: 'SourceKey' = "ltm_alpha"
    LTM_RISK: 'SourceKey' = "ltm_risk"
    LTM_STOP: 'SourceKey' = "ltm_stop"
    LTM_END: 'SourceKey' = "ltm_end"
    COMMON: 'SourceKey' = "common"
    @classmethod
    def from_str(cls, label) :
        label = label.lower()
        if label in ('rsi_alpha'):
            return SourceKey.RSI_ALPHA
        elif label in ('rsi_risk'):
            return SourceKey.RSI_RISK
        elif label in ('rsi_profit_percent'):
            return  SourceKey.RSI_PROFIT_PERCENT
        elif label in ('rsi_max_days'):
            return  SourceKey.RSI_MAX_DAYS
        elif label in ('rsi_stop'):
            return SourceKey.RSI_STOP
        elif label in ('rsi_end'):
            return SourceKey.RSI_END
        elif label in ('ltm_alpha'):
            return SourceKey.LTM_ALPHA
        elif label in ('ltm_risk'):
            return SourceKey.LTM_RISK
        elif label in ('ltm_stop'):
            return SourceKey.LTM_STOP
        elif label in ('ltm_end'):
            return SourceKey.LTM_END
        elif label in ('common'):
            return SourceKey.COMMON
        else:
            Main.qcMain.Error("missing key in enum " + str(label))
            raise NotImplementedError


class AlgoKey(Enum):
    RSI: 'AlgoKey' = "rsi"
    LTM: 'AlgoKey' = "ltm"
    COMMON: 'AlgoKey' = "common"
    @classmethod
    def from_str(cls, label) :
        label = label.lower()
        if label in ('rsi'):
            return cls.RSI
        elif label in ('ltm'):
            return cls.LTM
        elif label in ('common'):
            return cls.COMMON
        else:
            Main.qcMain.Error("missing key in enum " + str(label))
            raise NotImplementedError

