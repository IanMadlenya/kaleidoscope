import collections
import random

import pandas as pd

from kaleidoscope.account import Account
from kaleidoscope.globals import OrderStatus
from kaleidoscope.options.iterator.option_chain import OptionChainIterator


class BaseBroker(object):
    def __init__(self, datafeed, comm_model, margin_model, queue):

        self.order_list = collections.OrderedDict()

        self.datafeed = datafeed
        self.account = None

        self.comm_model = comm_model
        self.margin_model = margin_model

        # raw options chain data dict
        self.data = {}
        self.data_stream = None

        # events queue to send order events to
        self.queue = queue
        self.quotes = None

        self.continue_backtest = True
        self.current_date = None

    def open_account(self, cash=10000):
        self.account = Account(cash)

    def set_account_balance(self, balance):
        self.account.set_cash(balance)

    def source(self, symbol, start=None, end=None,
               exclude_splits=True, option_type=None
               ):
        """
        Get the option chain data from data source and store in data dict

        :param symbol: symbol to construct datafeed for
        :param start: start date to get options data for
        :param end: end date to get options data for
        :param exclude_splits: exclude options created as result of stock split, default True
        :param option_type: source a specific option type
        :return:
        """

        if symbol not in self.data:
            try:
                # we don't have raw option prices for this symbol yet, get it from data source
                self.data[symbol] = self.datafeed.get(symbol, start, end, exclude_splits, option_type)
            except IOError:
                raise

        # now that we added a new symbol, merge it into the data stream
        self.data_stream = self._merge_sources()

    def _merge_sources(self):

        df = pd.concat(self.data, ignore_index=True)
        # create an iterator to iterate over all data by quote_data
        return OptionChainIterator(df)

    def stream_next(self):
        """
        Return the next quote date's data event from all subscribed symbol

        :return: A bar event object containing the bar data for all subscribed symbols
        """
        try:
            data_event = next(self.data_stream)
        except StopIteration:
            self.continue_backtest = False
            return

        # update the current state for the broker and it's orders
        self.current_date = data_event.date
        self.update(data_event.quotes)

        # Send event to queue
        self.queue.put(data_event)

    def generate_ticket(self):
        """
        Returns a ticket number based on the current orders already
        processed by the broker.

        """
        return random.randint(100000, 999999)

    def update(self, quotes):
        """
        Using fresh quotes from data source, update current values
        for pending orders and positions held in accounts.

        :param quotes: fresh quotes in DataFrame format
        """
        self.quotes = quotes.fetch()

        # update the account's position values
        self.account.update(self.quotes)

        # check for expiring positions and orders
        self._check_expiration()

        # update the broker's working orders' option prices
        for order_item in self.order_list:
            order = self.order_list[order_item]
            if order.status == OrderStatus.WORKING:
                order.update(self.quotes)
                self.execute_order(order)

        self.status()

    def _check_expiration(self):
        """
        Remove positions expiring OTM or close positions at market price
        for positions expiring ITM.

        :param date: Current date, to check against positions' expiration date
        :return: A list of expiring positions
        """

        # find non-expired positions
        active = list()
        expired = False

        for p in self.account.positions:
            if self.current_date != p.get_expiration():
                active.append(p)
            else:
                self.account.cash += p.net_liquidating_value
                expired = True

        self.positions = active
        return expired

    def process_order(self, event):
        raise NotImplementedError("Subclass process_order method!")

    def execute_order(self, order):
        raise NotImplementedError("Subclass execute_order method!")

    def status(self):
        """
        Print information about the broker and its account's current state
        :return: None
        """

        working_orders = sum(1 for o in self.order_list
                             if self.order_list[o].status == OrderStatus.WORKING)
        open_positions = sum(1 for p in self.account.positions)

        net_liq_val = self.account.net_liquidating_value
        cash = self.account.cash
        buying_power = self.account.option_buying_power

        print(f"Date: {self.current_date}, "
              f"Cash: {cash:0.2f}, Net Liquidating Value: {net_liq_val:0.2f},"
              f" Option Buying Power: {buying_power:0.2f}"
              f" Working Orders: {working_orders}, Open Positions: {open_positions}"
              )

    def print_results(self):
        """
        Print information displayed when simulation ends
        :return: None
        """

        net_liq_val = self.account.net_liquidating_value
        cash = self.account.cash
        buying_power = self.account.option_buying_power

        print(f"Equity: {cash:0.2f},"
              f" Total P/L: {net_liq_val-self.account.initial_cash:0.2f}\n"
              )
