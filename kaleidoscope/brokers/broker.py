import pandas as pd
from kaleidoscope.options.iterator.option_chain import OptionChainIterator


class Broker(object):
    def __init__(self, account, datafeed, queue):
        # set the data source to be the datafeed passed in
        self.datafeed = datafeed
        # raw options chain data dict
        self.data = {}
        self.data_stream = None
        # events queue to send order events to
        self.queue = queue
        # set the account this brokerage can access
        self.account = account
        # hold continue backtest loop condition
        self.continue_backtest = True

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
            print('getting option chain data for %s' % symbol)
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

        # Send event to queue
        self.queue.put(data_event)

    def buy(self):
        raise NotImplementedError("Subclass buy method!")

    def sell(self):
        raise NotImplementedError("Subclass sell method!")

    def execute_order(self, event):
        raise NotImplementedError("Subclass execute_order method!")


class DefaultBroker(Broker):
    def __init__(self, account, datafeed, queue):
        super().__init__(account, datafeed, queue)

    def buy(self):
        pass

    def sell(self):
        pass

    def execute_order(self, event):
        pass
