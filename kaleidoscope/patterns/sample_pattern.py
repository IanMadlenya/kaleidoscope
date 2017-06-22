# pylint: disable=E1101
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
            "end_date": date(2016, 2, 19),
            "root": "VXX"  # do not analyze option splits
        }

        self.datafeed.subscribe_options("VXX", **params)

    def setup(self, quote_date, option_chains):
        """
        Perform custom strategic logic to isolate option chains and
        construct spreads to analyse for each quote date.
        """

        # Query and return a dataframe with call options expiring within the next 7 weeks
        options = option_chains['VXX'].lte('expiration', Period.SEVEN_WEEKS).fetch()

        # Batch create vertical call spreads on all strikes
        bear_call_spreads = OptionStrategies.vertical_spread(options, self.SPREAD_WIDTH)

        return bear_call_spreads

    def main(self, test_chain, test_spreads):
        """
        Perform custom analysis logic with the test_chain and test_spreads
        created from the setup method of this Pattern.

        :param test_chain: The full set of option chains to test with
        :param test_spreads: A list of test cases(spreads) to test with
        :return: TestResult object containing the test results

        """
        pass

    def plot(self):
        """

        :return:
        """
        pass

