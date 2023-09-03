
from AlgorithmImports import *

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.state.keys import AlgoKey
from frameworkAlgo.state.stateManager import StateManager


class ManualUniverseCreator():

    @classmethod
    def createManualUniverse(cls, algoKey: AlgoKey, symbols: List[Symbol]):

        Main.qcMain.UniverseSettings.Resolution = Resolution.Daily
        Main.qcMain.UniverseSettings.DataNormalizationMode = DataNormalizationMode.Raw
        StateManager.getInstance().addUniverse(algoKey, symbols)
        Main.log("Universe Symbols " + str(symbols))
        return ManualUniverseSelectionModel(symbols)
