"""
Module doc string
"""
import pandas as pd
pd.set_option('display.max_rows', 5000)

class Kaleidoscope(object):

    def __init__(self, option_feed=None):
        """
        Constructor for kaleidoscope object to process
        options data.
        """
        self.option_feed = option_feed
        self.pattern = None

        self.test_chains = None

        print("hello from kaleidoscope!")

    def add_option_feed(self, datafeed):
        """ Sets this instance to use provided datafeed object """
        self.option_feed = datafeed

    def add_pattern(self, pattern, **kwargs):
        """
        Adds a Pattern class for optimization.
        Instantiation will happen during run time. Args and kwargs MUST BE tuples
        which hold the values to check.

        Example: if a Pattern accepts a parameter period, for optimization purposes
        the call to add_pattern looks like:

        kaleidoscope.add_pattern(MyPattern, period=(15, 25))
        This will execute an optimization for values 15 and 25.
        """
        self.pattern = pattern(**kwargs)

    def add_opt_pattern(self, pattern, **kwargs):
        """
        Adds a Pattern class for optimization.
        Instantiation will happen during run time. Args and kwargs MUST BE iterables
        which hold the values to check.

        kaleidoscope.add_opt_pattern(MyPattern, period=range(15, 25))
        will execute MyPattern with period values 15 -> 25 (25 not included,
        because ranges are semi-open in Python)

        If a parameter is passed but shall not be optimized the call looks like:

        kaleidoscope.add_opt_pattern(MyPattern, period=(15,))
        Notice that period is still passed as an iterable ... of just 1 element
        """
        self.pattern = pattern(**kwargs)

    def run(self, mode='stats'):
        """
        Here we split the full option chain imported from the datafeed
        by the quote date and pass in the daily option chain data to the
        pattern to be processed.

        The Pattern will be responsible for constructing the option strategies
        based on various parameters for all strikes of the option chain.

        This method will then determine the trading result for each option spread
        created in the Pattern.
        """
        # process each quote date and pass option chain to pattern

        quote_list = []

        for quote_date in self.option_feed.date_stream:
            option_chain = self.option_feed.get_option_chains(quote_date)
            quote_list.append(self.pattern.main(quote_date, option_chain))

        self.test_chains = pd.concat(quote_list, axis=0, ignore_index=True, copy=False)
        self.test_chains.sort_values(['spread_symbol', 'quote_date', 'expiration'], ascending=[True, True, True], inplace=True)
        #self.test_chains = self.test_chains.set_index('spread_symbol')

        print(len(self.test_chains['spread_symbol'].unique()))
        #print(self.test_chains[self.test_chains['spread_symbol'] == '.VXX160219C00018000-.VXX160219C00020000'])

        if mode == 'backtest':
            # perform backtest with option chains, run each spread with a starting account balance
            # at start of trading or starting and ending on a specific time interval
            pass
        elif mode == 'stats':
            # perform analysis on option chains and return stats
            pass
