from unittest import TestCase

import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal

import kaleidoscope as kd
from kaleidoscope.datas import opt_params
from kaleidoscope.globals import OptionType, Period
from kaleidoscope.options.option_query import OptionQuery
from kaleidoscope.options.option_strategies import OptionStrategies


class TestOptionStrategies(TestCase):
    def setUp(self):

        self.start = '2016-02-19'
        self.end = '2016-02-19'

        self.shift_col = [(col[0], col[3]) for col in opt_params if col[2] == 1 and col[1] != -1]

        # Retrieve all options with specified DTE and expiration dates
        self.data = kd.get('VXX', start=self.start, end=self.end)
        self.dates = sorted(self.data.keys())

        self.output_list = []
        self.test_chain_list = {}

        for quote_date in self.dates:
            option_qy = OptionQuery(self.data[quote_date])
            chains = option_qy.lte('expiration', Period.SEVEN_WEEKS).fetch()
            self.test_chain_list[quote_date] = chains
            self.output_list.append(chains)

        # output a list of inputs for trace
        test_fixture = pd.concat(self.output_list, ignore_index=True)
        test_fixture.output_to_csv("generate_offsets_inputs_%s" % self.end)

    def test_generate_offsets(self):
        """
        This test method will create a test case for each possible spread widths within a set of strikes
        for each quote date under the specified expiry cycles.
        :return:
        """

        # hold all the intervals tested to avoid duplicating tests
        all_widths = []

        for quote_date in self.test_chain_list:
            with self.subTest(quote_date=quote_date):
                # filter for current quote_date's data and option type
                option_qy = OptionQuery(self.test_chain_list[quote_date])
                call_chains = option_qy.option_type(OptionType.CALL).fetch()
                put_chains = option_qy.option_type(OptionType.PUT).fetch()

                # get all unique strikes for the date's option chains
                call_strikes = call_chains['strike'].unique()
                put_strikes = put_chains['strike'].unique()

                if not np.array_equal(call_strikes, put_strikes):
                    raise ValueError('Call and put strikes not equal. Please review option chain data.')
                else:
                    all_strikes = call_strikes

                # Get all interval values between each strike
                num_of_strikes = len(all_strikes)
                widths = []

                # calculate all possible widths for this set of strikes
                for i in range(0, num_of_strikes):
                    for j in range(i + 1, num_of_strikes):
                        interval = all_strikes[j] - all_strikes[i]
                        if interval not in all_widths:
                            widths.append(interval)
                            all_widths.append(interval)

                for width in widths:
                    with self.subTest(width=width):
                        # for each quote date and width, generate a result fixture
                        expected_offsets_call = self.generate_fixtures(call_chains.copy(), OptionType.CALL, width)
                        expected_offsets_put = self.generate_fixtures(put_chains.copy(), OptionType.PUT, width)

                        # test each generated fixtures with dynamically created test case
                        actual_offsets_call = OptionStrategies.generate_offsets(call_chains.copy(),
                                                                                width,
                                                                                OptionType.CALL)

                        actual_offsets_put = OptionStrategies.generate_offsets(put_chains.copy(),
                                                                               width,
                                                                               OptionType.PUT)

                        try:
                            assert_frame_equal(actual_offsets_call, expected_offsets_call,
                                               check_dtype=False,
                                               check_exact=True,
                                               check_datetimelike_compat=True
                                               )
                        except AssertionError:
                            actual_offsets_call.output_to_csv("test_generate_offset_actual_%s_C" % width)
                            expected_offsets_call.output_to_csv("test_generate_offset_expected_%s_C" % width)
                            raise

                        try:
                            assert_frame_equal(actual_offsets_put, expected_offsets_put,
                                               check_dtype=False,
                                               check_exact=True,
                                               check_datetimelike_compat=True
                                               )
                        except AssertionError:
                            actual_offsets_call.output_to_csv("test_generate_offset_actual_%s_P" % width)
                            expected_offsets_call.output_to_csv("test_generate_offset_expected_%s_P" % width)
                            raise

    def generate_fixtures(self, chains, option_type, width):
        """
        Return a DataFrame object representing the expected results of the generate_offset function
        for the specified width and option type for a set of option chains.

        :param chains:
        :param option_type:
        :param width:
        :return:
        """
        chains['strike_key'] = chains['strike'] + (width * option_type.value[1])

        chains = chains.merge(chains, left_on='strike_key', right_on='strike', suffixes=('', '_shifted'))
        chains = chains.drop(['strike_key', 'strike_key_shifted', 'quote_date_shifted', 'expiration_shifted',
                              'option_type_shifted', 'underlying_price_shifted'], axis=1)

        return chains
