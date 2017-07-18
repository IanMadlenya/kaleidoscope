import collections
import itertools
import time
import queue

from .brokers.broker import DefaultBroker
from .commissions import Commission
from .sizers.sizer_dollar_amt import SizerDollarAmount
from .events import EventType
from .account import Account
from kaleidoscope.data import get


class Backtest(object):
    def __init__(self, broker=None, cash=10000, commissions=None, sizer=None):

        self.data = None
        self.cash = cash
        self.broker = DefaultBroker if broker is None else broker
        self.account = Account
        self.comm = Commission.default_commissions if commissions is None else commissions
        self.sizer = SizerDollarAmount if sizer is None else sizer

        self.strats = list()
        self.events_queue = queue.Queue()

    def add_data(self, data):
        """
        Takes an OptionSeries object returned by internal 'get' method
        and assigns to backtest as data attribute.

        :param data: The data (OptionSeries) to use for this backtest session
        """
        self.data = data

    def get_data(self, ticker, start, end,
                 provider=None, path=None,
                 include_splits=False, option_type=None):
        """
        Calls the internal 'get' method to retrieve option chain data from
        data source and stores it in this instance of backtester.

        :param ticker: the symbol to download
        :param start: expiration start date of downloaded data
        :param end: expiration end date of downloaded data
        :param provider: The data source to use for downloading data, reference to function
                         Defaults to sqlite database
        :param path: Path to the data source
        :param include_splits: Should data exclude options created from the underlying's stock splits
        :param option_type: If None, or not passed in, will retrieve both calls and puts of option chain
        :return: Dataframe containing all option chains as filtered by algo for the specified date range
        """
        self.data = get(ticker, start, end, provider, path, include_splits, option_type)

    def add_strategy(self, strategy, **kwargs):
        """
        Adds a ``Strategy`` class to the mix for a single pass run.
        Instantiation will happen during ``run`` time.
        args and kwargs will be passed to the strategy as they are during
        instantiation.

        :param strategy: strategy object to test with
        :param kwargs: params to pass to strategy on runtime
        :return:
        """

        self.strats.append((strategy, kwargs))

        # here we return the index to refer to the strategy incase we want to
        # add or reference this strategy e.g. adding specific sizer for this strat
        return len(self.strats) - 1

    def add_opt_strategy(self, strategy, **kwargs):
        """
        Adds a Strategy class to the mix for optimization. Instantiation
        will happen during run time.
        kwargs MUST BE iterables which hold the values to check.

        :param strategy: strategy object to test with
        :param kwargs: iterables which hold the values to optimize.
        :return:
        """

        # apply cartesian product of all params to generate all combinations of strategies to test for
        opt_keys = list(kwargs)

        vals = self.iterize(kwargs.values())
        opt_vals = itertools.product(*vals)

        o_kwargs1 = map(zip, itertools.repeat(opt_keys), opt_vals)
        opt_kwargs = map(dict, o_kwargs1)

        it = itertools.product([strategy], opt_kwargs)
        for strat in it:
            self.strats.append(strat)

    def add_sizer(self, sizer, **kwargs):
        """
        Adds a Sizer that will be applied to any strategy added to backtester.
        This would be the default sizer for all strategies.

        :param sizer: sizer class
        :param kwargs: params to pass to sizer
        :return:
        """

        # initialize a new instance of specified sizer with kwargs
        self.sizer = sizer(**kwargs)

    def add_sizer_by_idx(self, idx, sizer, **kwargs):
        """
        Adds a Sizer that will be applied to the strategy referenced by the index.

        :param idx: the index referring to the strategy to apply the sizer to
        :param sizer: sizer class
        :param kwargs: params to pass to sizer
        :return:
        """
        pass

    @staticmethod
    def iterize(iterable):
        """
        Handy function which turns things into things that can be iterated upon
        including iterables

        :param iterable:
        """
        niterable = list()
        for elem in iterable:
            if isinstance(elem, str):
                elem = (elem,)
            elif not isinstance(elem, collections.Iterable):
                elem = (elem,)

            niterable.append(elem)

        return niterable

    def run(self):

        self.account = self.account(self.cash)
        self.sizer = self.sizer()

        # initialize broker with data
        self.broker = self.broker()

        # program timer
        program_starts = time.time()

        for scenario in self.strats:
            # initialize a new instance strategy from the strategy list
            # this step will create the necessary spread prices from option data
            # and store it in the broker's strat_data list containing OptionSeries objects
            strategy = scenario[0](self.broker, **scenario[1])

            # run backtesting loop
            try:
                event = self.events_queue.get(False)
            except queue.Empty:
                self.broker.stream_next()
            else:
                if event is not None:
                    if event.type == EventType.BAR:
                        strategy.on_data(event)
                        self.account.update_account(event)
                        # self.statistics.update(event.time, self.portfolio_handler)
                    elif event.type == EventType.ORDER:
                        self.broker.execute_order(event)
                    elif event.type == EventType.FILL:
                        self.account.on_fill(event)
                    else:
                        raise NotImplemented("Unsupported event.type '%s'" % event.type)

        print(len(self.broker.strat_data))
        program_ends = time.time()
        print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))
