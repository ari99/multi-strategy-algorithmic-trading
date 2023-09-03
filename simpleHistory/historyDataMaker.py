from typing import List
import io

from simpleHistory.transaction import Transaction

def makeTickers() -> List[str]:
    transactions: List[Transaction] = Transaction.readTransactions("./transactionsFiltered.csv")
    tickers: List[str] = []
    for transaction in transactions:
        ticker: str = transaction.ticker
        if ticker not in tickers:
            tickers.append(ticker)

    return tickers

def writeTickers():
    tickers = makeTickers()
    with io.open('orderTickers2.txt', 'w') as f:
        f.writelines(line + "," for line in tickers)


def readTickers():
    tickers = []
    with open('orderTickers.txt', 'r') as f:
        tickers = [line.rstrip(u'\n') for line in f]
    return tickers



if __name__ == "__main__":
    writeTickers()