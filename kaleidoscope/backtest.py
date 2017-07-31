import collections
import itertools
import queue
import time

from kaleidoscope.brokers.broker import DefaultBroker
from kaleidoscope.datafeeds.sqlite_data import SQLiteDataFeed
from kaleidoscope.sizers.sizers import FixedQuantitySizer
from kaleidoscope.commissions import Commission
from kaleidoscope.account import Account
from kaleidoscope.event import EventType


class Backtest(object):
    def __init__(self, broker=DefaultBroker,
                 data=SQLiteDataFeed,
                 data_path=None
                 ):

        # setup backtest private variables
        self.data = None
        self.strats = list()
        self.queue = queue.Queue()

        # initialize backtest configuration
        self.account = Account()
        self.datafeed = data(data_path)
        self.broker = broker(self.account, self.datafeed, self.queue)
        self.sizer = FixedQuantitySizer(self.account)

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

        # program timer
        program_starts = time.time()

        for scenario in self.strats:
            # initialize a new instance strategy from the strategy list
            # this step will create the necessary spread prices from option data
            # and store it in the broker's strat_data list containing OptionSeries objects
            strategy = scenario[0](self.broker, self.account, self.queue, **scenario[1])
            self.broker.continue_backtest = True

            while self.broker.continue_backtest:
                # run backtesting loop
                try:
                    event = self.queue.get(False)
                except queue.Empty:
                    self.broker.stream_next()
                else:
                    if event is not None:
                        if event.type == EventType.DATA:
                            strategy.current_date = event.date
                            strategy.on_data(event.quotes)
                            self.account.update_account(event)
                        elif event.type == EventType.ORDER:
                            self.broker.execute_order(event)
                        elif event.type == EventType.FILL:
                            self.account.on_fill(event)
                            strategy.on_fill_event(event)
                        else:
                            raise NotImplementedError("Unsupported event.type '%s'" % event.type)

        program_ends = time.time()
        print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))
