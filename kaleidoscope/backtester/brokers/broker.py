from kaleidoscope.options.option_strategies import construct
from kaleidoscope.data import get


class Broker(object):
    def __init__(self, path=None):
        # raw options chain data
        self.data = {}
        # list of OptionSeries holding historic options prices
        self.strat_data = []
        # set broker account to have default balance of 10000
        self.cash = 10000
        # path of data source on file
        self.path = path
        # hold continue backtest loop condition
        self.continue_backtest = True

    def source(self, symbol, strat, start, end, **params):
        """
        Create the option spread price data and store it in the strat_data list

        :param symbol: symbol to construct datafeed for
        :param strat: option strategy to create price data for
        :param start: start date to get options data for
        :param end: end date to get options data for
        :param params: params to create option strategy
        :return:
        """

        if symbol not in self.data:
            print('no raw option data for %s' % symbol)
            # we don't have raw option prices for this symbol yet, get it from data source
            self.data[symbol] = get(symbol, start, end, provider=self.path)

        has_strat_data = False
        for strat_data in self.strat_data:
            # need to check symbol, strategy, params match the current strat_data object(optionSeries) attr
            if strat_data.symbol == symbol and \
                            strat_data.strategy == strat.__name__ and \
                            strat_data.params == params:
                has_strat_data = True

        if not has_strat_data:
            # create the option spreads as per strategy
            print('creating %s spreads with' % strat.__name__, params)
            spreads = construct(symbol, strat, self.data[symbol], **params)
            self.strat_data.append(spreads)

    def stream_next(self, symbol):
        """
        Return the next bar event from the requested symbol

        :param symbol: symbol to get next bar for
        :return:
        """

        # try:
        #     index, row = next(self.bar_stream)
        # except StopIteration:
        #     self.continue_backtest = False
        #     return
        # # Obtain all elements of the bar from the dataframe
        # ticker = row["Ticker"]
        # period = 86400  # Seconds in a day
        # # Create the tick event for the queue
        # bev = self._create_event(index, period, ticker, row)
        # # Store event
        # self._store_event(bev)
        # # Send event to queue
        # self.events_queue.put(bev)
        pass


class DefaultBroker(Broker):
    def __init__(self):
        super().__init__()

    def buy(self):
        pass

    def sell(self):
        pass
