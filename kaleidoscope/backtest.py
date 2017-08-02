import collections
import itertools
import queue
import time

from kaleidoscope.account import Account
from kaleidoscope.brokers.default_broker import DefaultBroker
from kaleidoscope.comm import DefaultCommissions
from kaleidoscope.datafeeds.sqlite_data import SQLiteDataFeed
from kaleidoscope.event import EventType
from kaleidoscope.margin import ThinkOrSwimMargin


class Backtest(object):
    def __init__(self, broker=DefaultBroker,
                 comm=DefaultCommissions,
                 margin=ThinkOrSwimMargin,
                 data=SQLiteDataFeed,
                 data_path=None
                 ):

        # setup backtest private variables
        self.data = None
        self.strats = list()
        self.queue = queue.Queue()

        # initialize backtest configuration
        self.datafeed = data(data_path)
        self.comm = comm()
        self.margin = margin()
        self.broker = broker(self.datafeed, self.comm, self.margin, self.queue)

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
            # and an account instance for each scenario
            self.broker.set_account(Account())
            strategy = scenario[0](self.broker, self.queue, **scenario[1])
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
                            # update account values with current data
                            self.broker.account.update_account(event)
                            # update broker with current data
                            self.broker.update_data_event(event)
                            # update strategy instance with current data
                            strategy.on_data_event(event)
                        elif event.type == EventType.ORDER:
                            self.broker.execute_order(event)
                        elif event.type == EventType.FILL:
                            self.broker.account.process_order(event)
                            strategy.on_fill_event(event)
                        else:
                            raise NotImplementedError("Unsupported event.type '%s'" % event.type)

        program_ends = time.time()
        print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))
