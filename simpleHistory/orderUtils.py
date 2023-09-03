#region imports
from AlgorithmImports import *
#endregion
from System.Collections import IEnumerable

from typing import List


# https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-management/transaction-manager
class OrderUtils:

    def __init__(self, main: QCAlgorithm) -> None:
        self.main = main

    def getLastOrderTicket(self) -> OrderTicket:
        order_id = self.main.Transactions.LastOrderId
        ticket = self.main.Transactions.GetOrderTicket(order_id)
        return ticket

    def getOrders(self, symbol: Symbol):
        # Get all order tickets
        order_tickets: IEnumerable= self.main.Transactions.GetOrderTickets()

        # Get order tickets that pass a filter
        filtered_order_tickets = self.main.Transactions.GetOrderTickets(lambda order_ticket: OrderTicket.Symbol == symbol)

        # Get all open order tickets
        open_order_tickets = self.main.Transactions.GetOpenOrderTickets()

        # Get all open order tickets for a symbol
        symbol_open_order_tickets = self.main.Transactions.GetOpenOrderTickets(symbol)

        # Get open order tickets that pass a filter
        filtered_open_order_tickets = self.main.Transactions.GetOpenOrderTickets(
            lambda order_ticket: order_ticket.Quantity > 10)


    def getOpenOrders(self, symbol: Symbol):
        # Get all open orders
        all_open_orders = self.main.Transactions.GetOpenOrders()

        # Get all open orders that pass a filter
        filtered_open_orders = self.main.Transactions.GetOpenOrders(lambda x: x.Quantity > 10)

        # Retrieve a list of all open orders for a symbol
        symbol_open_orders: List[Order] = self.main.Transactions.GetOpenOrders(symbol)

    def getRemainingOrderQuantity(self, symbol: Symbol):
        # Get the quantity of all open orders
        all_open_quantity = self.main.Transactions.GetOpenOrdersRemainingQuantity()

        # Get the quantity of open orders that pass a filter
        filtered_open_quantity = self.main.Transactions.GetOpenOrdersRemainingQuantity(
            lambda order_ticket: order_ticket.Quantity > 10
        )

        # Get the quantity of open orders for a symbol
        symbol_open_quantity = self.main.Transactions.GetOpenOrdersRemainingQuantity(symbol)

    def cancelOrders(self):
        # Cancel all open orders
        all_cancelled_orders = self.main.Transactions.CancelOpenOrders()

        # Cancel orders related to IBM and apply a tag
        ibm_cancelled_orders = self.main.Transactions.CancelOpenOrders("IBM", "Hit stop price")