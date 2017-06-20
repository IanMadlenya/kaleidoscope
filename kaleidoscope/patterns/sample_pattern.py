#pylint: disable=E1101
from datetime import datetime

from kaleidoscope.patterns.base_pattern import BasePattern
from kaleidoscope.options.option_strategies import OptionStrategies
from kaleidoscope.globals import Period

class SamplePattern(BasePattern):
    """
    This is a simple analysis pattern used to demonstrate a simple use case
    of gathering data points for bear call spread on the VXX every thursday
    and generating statistics on its prices through time.
    """

    def init(self):
        pass

    def main(self, date, option_chain):
        """
        Perform logic to isolate option chains to analyse
        """
        # Query and return a dataframe with call options expiring in the next 7 weeks
        options = option_chain['VXX'].call().fetch()

        # Batch create bear calls spreads on all strikes
        bear_call_spreads = OptionStrategies.vertical_spread(options, self.SPREAD_WIDTH)

        return bear_call_spreads



