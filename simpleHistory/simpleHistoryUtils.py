#region imports
from AlgorithmImports import *
#endregion

from simpleHistory.transaction import Transaction
import csv
from typing import List


class SimpleHistoryUtils:

    def readTransactions(self, inputPath: str) -> List[Transaction]:
        allRows: List[Transaction] = []
        with open(inputPath, newline='') as csvfile:
            reader = csv.reader(csvfile)  # , delimiter=' ', quotechar='|')
            for row in reader:
                transaction: Transaction = Transaction.createFromCombinedHistoryRow(row)
                allRows.append(transaction)
            return allRows

    def addSecurityIdToTransactions(self, transactions: List[Transaction]) -> List[Transaction]:
        newTransactions: List[Transaction] = []
        for transaction in transactions:
            ticker = transaction.ticker
            resolveDate = transaction.makeDateTime()

            # https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/security-identifiers?ref=v1
            securityId = SecurityIdentifier.GenerateEquity(
                            ticker, Market.USA, mappingResolveDate=resolveDate)  #datetime(2021, 12, 1))
            transaction.securityId = securityId
            newTransactions.append(transaction)

        return newTransactions
