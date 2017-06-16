#pylint: disable=E1101
from datetime import datetime

from kaleidoscope.patterns.base_pattern import BasePattern
from kaleidoscope.options.option_strategies import OptionStrategies
from kaleidoscope.globals import Period

class SamplePattern(BasePattern):
    """
    This is a simple analysis pattern used to demonstrate a simple use case
    of gatherin data points for bear call spread on the VXX every thursday
    and generating statistics on its prices through time.
    """
    def process_option_chain(self, date, option_chain):
        """
        Perform logic to isolate option chains to analyse
        """
        # Query and return a dataframe with call options expiring in the next 7 weeks
        options = option_chain['VXX'].closest('expiration', Period.SEVEN_WEEKS).call().fetch()

        # Batch create bear calls spreads on all strikes
        bear_call_spreads = OptionStrategies.vertical_spread(options, self.SPREAD_WIDTH)

        # get expiration date of this chain
        first_row = bear_call_spreads.iloc[:1, 0:2]
        expiration = datetime.strftime(first_row.iloc[0][1], '%Y-%m-%d')

        # store this day's option chain into basis dict
        datas = (expiration, bear_call_spreads)
        self.basis[date] = datas

    def merge_option_chains(self):
        """
        This method will merge all option chains stored in the basis into one
        dataframe that contains all option chains for all dates. This is used
        for plotting purposes
        """
        pass

