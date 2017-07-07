import os
from unittest import TestCase

import pandas as pd
from pandas.util.testing import assert_frame_equal

import kaleidoscope as kd
from kaleidoscope.datas import opt_params
from kaleidoscope.globals import OptionType, Period, PROJECT_DIR, TEST_DIR, FIXTURES
from kaleidoscope.options.option_query import OptionQuery
from kaleidoscope.options.option_strategies import OptionStrategies


class TestOptionStrategies(TestCase):
    def setUp(self):
        # Retrieve all options with DTE for 2016-02-19 for testing
        self.data_2016_02_19 = kd.get('VXX', start='2016-02-19', end='2016-02-19')

    def test_generate_offsets_w_2_C_2016_02_19(self):

        # TEST quote_date of 2016-02-19 =====================================================
        # here we are testing the offsets generated for the last trading day for
        # options with DTE of 2016-02-19. This test case tests for regular and
        # irregular strike intervals

        test_width = 2
        test_quote_date_1 = '2016-02-19'
        test_fixture_file = 'generate_offsets_w_2_C_2016_02_19_fixture.csv'
        path = os.path.join(os.sep, PROJECT_DIR, TEST_DIR, FIXTURES, test_fixture_file)

        try:
            test_fixture = pd.read_csv(path, index_col=0, parse_dates=['quote_date', 'expiration'])
        except:
            raise IOError('Cannot open fixture file')

        option_qy = OptionQuery(self.data_2016_02_19[test_quote_date_1])
        chains = (option_qy.lte('expiration', Period.SEVEN_WEEKS)
                  .option_type(OptionType.CALL)
                  .fetch()
                  )

        shift_col = [(col[0], col[3]) for col in opt_params if col[2] == 1 and col[1] != -1]
        sc = OptionStrategies.generate_offsets(chains, test_width, shift_col, OptionType.CALL)
        assert_frame_equal(sc, test_fixture,
                           check_dtype=False,
                           check_exact=True,
                           check_datetimelike_compat=True
                           )

    def test_generate_offsets_w_2_P_2016_02_19(self):

        # TEST quote_date of 2016-02-19 =====================================================
        # here we are testing the offsets generated for the last trading day for
        # options with DTE of 2016-02-19. This test case tests for regular and
        # irregular strike intervals

        test_width = 2
        test_quote_date_1 = '2016-02-19'
        test_fixture_file = 'generate_offsets_w_2_P_2016_02_19_fixture.csv'
        path = os.path.join(os.sep, PROJECT_DIR, TEST_DIR, FIXTURES, test_fixture_file)

        try:
            test_fixture = pd.read_csv(path, index_col=0, parse_dates=['quote_date', 'expiration'])
        except:
            raise IOError('Cannot open fixture file')

        option_qy = OptionQuery(self.data_2016_02_19[test_quote_date_1])
        chains = (option_qy.lte('expiration', Period.SEVEN_WEEKS)
                  .option_type(OptionType.PUT)
                  .fetch()
                  )

        shift_col = [(col[0], col[3]) for col in opt_params if col[2] == 1 and col[1] != -1]
        sc = OptionStrategies.generate_offsets(chains, test_width, shift_col, OptionType.PUT)
        assert_frame_equal(sc, test_fixture,
                           check_dtype=False,
                           check_exact=True,
                           check_datetimelike_compat=True
                           )
