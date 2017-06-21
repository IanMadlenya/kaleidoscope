#pylint: disable=E1101
from datetime import date
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
        """
        Define parameters to query option chain data from database. Also define any
        Pattern specific variables here
        :return: None
        """

        # define params to filter options retrieved from the database
        params = {
            "option_type": "c",
            "start_date": date(2016, 1, 4),
            "end_date": date(2016, 1, 4),
            "root": "VXX" # do not analyze option splits
        }

        self.datafeed.subscribe_options("VXX", **params)

    def setup(self, option_chains):
        """
        Perform logic to isolate option chains and construct spreads to analyse for each quote date
        """
        # Query and return a dataframe with call options expiring in the next 7 weeks
        options = option_chains['VXX'].fetch()

        # Batch create bear calls spreads on all strikes
        bear_call_spreads = OptionStrategies.vertical_spread(options, self.SPREAD_WIDTH)

        return bear_call_spreads

    def main(self, test_chain, test_spreads):
        """

        :param test_chain:
        :param test_spreads:
        :return:
        """
        pass


