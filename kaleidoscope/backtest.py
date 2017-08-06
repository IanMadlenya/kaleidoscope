import collections
import itertools
import queue
import time

from kaleidoscope.brokers.default_broker import DefaultBroker
from kaleidoscope.commissions import default_commissions
from kaleidoscope.datafeeds.sqlite_data import SQLiteDataFeed
from kaleidoscope.event import EventType
from kaleidoscope.margin import tos_margin


class Backtest(object):
    def __init__(self, broker=DefaultBroker,
                 commissions=default_commissions,
                 margin=tos_margin,
                 data=SQLiteDataFeed,
                 data_path=None
                 ):

        # setup backtest private variables
        self.data = None
        self.strats = list()
        self.queue = queue.Queue()

        # initialize backtest configuration
        self.datafeed = data(data_path)
        self.commissions = commissions
        self.margin = margin
        self.broker = broker(self.datafeed, self.commissions, self.margin, self.queue)

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
            self.broker.open_account()
            strategy = scenario[0](self.broker, self.queue,
                                   self.commissions, self.margin, **scenario[1]
                                   )
            self.broker.continue_backtest = True

            while self.broker.continue_backtest:
                # run backtesting loop
                try:
                    event = self.queue.get(False)
                except queue.Empty:
                    self.broker.stream_next()
                else:
                    if event is not None:
                        if event.event_type == EventType.DATA:
                            # update strategy instance with current data
                            strategy.on_data_event(event)
                        elif event.event_type == EventType.ORDER:
                            # send the order to the broker for processing
                            self.broker.process_order(event)
                        elif event.event_type == EventType.FILL:
                            # notify the strategy that we have a fill on one of its orders
                            strategy.on_fill_event(event)
                        elif event.event_type == EventType.REJECTED:
                            strategy.on_rejected_event(event)
                        elif event.event_type == EventType.EXPIRED:
                            strategy.on_expired_event(event)
                        else:
                            raise NotImplementedError("Unsupported event.type '%s'" % event.type)

            # reached the end of simulation, print results
            print(f"Results for {strategy.name} =======================================================")
            self.broker.print_results()

        program_ends = time.time()
        print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))
