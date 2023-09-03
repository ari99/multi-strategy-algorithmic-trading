#region imports
import csv
from datetime import datetime
from typing import List, Dict

from QuantConnect import Symbol


#endregion

# Your New Python File
class Transaction:
    historyDateFormat = "%Y-%m-%d"

    def __init__(self):
        self.id = 0
        self.date = ""
        self.action = ""
        self.ticker = ""
        self.securityId = None
        self.description = ""
        self.quantity = ""
        self.price = ""
        self.fees = ""
        self.amount = ""

    def __str__(self):
        res = (str(self.id) + " Date: "+ self.date + " Action: " + self.action +
               " Ticker:  " + self.ticker + " SecId: " + self.securityId.ToString() + # " Desc " +self.description +
               " Quantity: " + self.quantity + " price: " + self.price)
        return res

    def __repr__(self):
        res = ("< " + str(self.id) + " Date: "+ self.date + " Action: " + self.action +
               " Ticker:  " + self.ticker + " SecId: " + self.securityId.ToString() + # " Desc " +self.description +
               " Quantity: " + self.quantity + " price: " + self.price + " > ")
        return res

    def makeDateTime(self) -> datetime:
        return datetime.strptime(self.date, Transaction.historyDateFormat)
        #sliceTimeStr: str = time.strftime(Transaction.historyDateFormat)



    # https://realpython.com/python-multiple-constructors/
    # https://stackoverflow.com/questions/4613000/difference-between-cls-and-self-in-python-classes
    # https://stackoverflow.com/questions/141545/how-to-overload-init-method-based-on-argument-type
    @classmethod
    def createFromHistoryRow(cls, row):
        transaction = Transaction()
        transaction.date = row[0]
        transaction.action = row[1]
        transaction.ticker = row[2]
        transaction.description = row[3]
        transaction.quantity = row[4]
        transaction.price = row[5]
        transaction.fees = row[6]
        transaction.amount = row[7]
        return transaction

    @classmethod
    def createFromCombinedHistoryRow(cls, row):
        transaction = Transaction()
        transaction.id = row[0]
        transaction.date = row[1]
        transaction.action = row[2]
        transaction.ticker = row[3]
        transaction.description = row[4]
        transaction.quantity = row[5]
        transaction.price = row[6]
        transaction.fees = row[7]
        transaction.amount = row[8]
        return transaction

    def convertToCombinedHistoryRow(self) -> List:
        row = ["" for i in range(9)]
        row[0] = self.id
        row[1] = self.date
        row[2] = self.action
        row[3] = self.ticker
        row[4] = self.description
        row[5] = self.quantity
        row[6] = self.price
        row[7] = self.fees
        row[8] = self.amount
        return row

    def convertToHistoryRow(self) -> List:
        row = ["" for i in range(8)]
        row[0] = self.date
        row[1] = self.action
        row[2] = self.ticker
        row[3] = self.description
        row[4] = self.quantity
        row[5] = self.price
        row[6] = self.fees
        row[7] = self.amount
        return row

    @classmethod
    def readTransactions(cls, inputPath) -> None:
        allRows: List[Transaction] = []
        with open(inputPath, newline='') as csvfile:
            reader = csv.reader(csvfile)#, delimiter=' ', quotechar='|')
            for row in reader:
                transaction: Transaction = Transaction.createFromCombinedHistoryRow(row)
                allRows.append(transaction)
            return allRows

    def writeRows(self,outputPath, transactions: List) -> None:
        out = open(outputPath, "w")  # open text output
        writer = csv.writer(out)
        for transaction in transactions:
            writer.writerow(transaction.convertToCombinedHistoryRow())


    @classmethod
    def makeGroupTransactionsByDay(cls, transactions: List)-> Dict[str, List]:
        groups = {}
        for transaction in transactions:
            day = transaction.date
            if day in groups:
                groups[day].append(transaction)
            else:
                groups[day] = []
                groups[day].append(transaction)

        return groups

    @classmethod
    def makeGroupTransactionsByTicker(cls, transactions: List) -> Dict:
        groups = {}
        for transaction in transactions:
            symbol = transaction.ticker
            if symbol in groups:
                groups[symbol].append(transaction)
            else:
                groups[symbol] = []
                groups[symbol].append(transaction)

        return groups
