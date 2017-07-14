import time
import itertools
import collections

from kaleidoscope.backtester.commissions import Commission
from kaleidoscope.backtester.sizer import Sizer
from kaleidoscope.options.option_strategies import construct
from kaleidoscope.options.option_strategies import OptionStrategies
from kaleidoscope.data import get


class Backtest(object):
    def __init__(self, data=None, balance=10000,
                 commissions=Commission.tos, sizer=Sizer.quantity,
                 sizer_params=None, start=None, end=None):

        """

        :param data: The option spreads to run backtest for
        :param balance: The initial starting balance of the account
        :param commissions: The commission schedule to apply for each transaction
        :param sizer: The sizer function that determines the quantity to trade with
        :param sizer_params: Any params to pass into the sizer function
        :param start: start date of backtest if not same as option chain date range
        :param end: end date of backtest if not same as option chain date range
        :return: performance object containing the results of the backtest
        """
        self.data = data
        self.balance = balance
        self.comm = commissions
        self.sizer = sizer
        self.sizer_params = sizer_params
        self.start = start
        self.end = end

        self.strats = list()

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

        self.strats.append([strategy, kwargs])

    def add_opt_strategy(self, strategy, **kwargs):
        """
        Adds a Strategy class to the mix for optimization. Instantiation
        will happen during run time.
        kwargs MUST BE iterables which hold the values to check.

        :param strategy: strategy object to test with
        :param kwargs: iterables which hold the values to optimize.
        :return:
        """

        # apply cartesian product of all params to generate all combinations of
        # strategies to test for
        opt_keys = list(kwargs)

        vals = self.iterize(kwargs.values())
        opt_vals = itertools.product(*vals)

        o_kwargs1 = map(zip, itertools.repeat(opt_keys), opt_vals)

        opt_kwargs = map(dict, o_kwargs1)

        it = itertools.product([strategy], opt_kwargs)
        self.strats.append(it)

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

        program_ends = time.time()
        print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))
