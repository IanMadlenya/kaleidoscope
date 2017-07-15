import collections
import itertools
import time

from kaleidoscope.backtester.brokers import DefaultBroker
from kaleidoscope.backtester.commissions import Commission
from kaleidoscope.backtester.sizers.sizer_dollar_amt import SizerDollarAmount


class Backtest(object):
    def __init__(self):

        self.data = None

        self.broker = DefaultBroker()
        self.comm = Commission.default_commissions
        self.sizer = SizerDollarAmount()

        self.strats = list()

    def add_data(self, data):
        """
        Calls the internal 'get' method to retrieve option chain data from
        data source and stores it in this instance of backtester.

        :param data: The data to use for this backtest session
        """
        self.data = data

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

        self.strats.append([(strategy, kwargs)])

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
        self.strats.append(it)

    def add_sizer(self, sizer, **kwargs):
        """
        Adds a Sizer that will be applied to any strategy added to backtester.
        This would be the default sizer for all strategies.

        :param sizer: sizer class
        :param kwargs: params to pass to sizer
        :return:
        """
        pass

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

        if not self.data:
            return []  # nothing can be run

        # program timer
        program_starts = time.time()

        for strat in self.strats:
            strategy = strat[0]
            strat_run = strategy(strat[1])
            print(strat_run)

        program_ends = time.time()
        print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))
