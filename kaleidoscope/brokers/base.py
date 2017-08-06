import pandas as pd

from kaleidoscope.account import Account
from kaleidoscope.options.iterator.option_chain import OptionChainIterator


class BaseBroker(object):
    def __init__(self, datafeed, commissions, margin, queue):

        self.datafeed = datafeed
        self.account = None
        self.commissions = commissions
        self.margin = margin

        # raw options chain data dict
        self.data = {}
        self.data_stream = None

        # events queue to send order events to
        self.queue = queue

        self.continue_backtest = True
        self.current_date = None

    def open_account(self):
        self.account = Account()

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

    def update(self, quotes):
        raise NotImplementedError("Subclass update_data method!")

    def process_order(self, event):
        raise NotImplementedError("Subclass process_order method!")

    def execute_order(self, order):
        raise NotImplementedError("Subclass execute_order method!")
