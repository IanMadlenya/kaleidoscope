import math

import numpy as np
import pandas as pd

from kaleidoscope.datas import opt_params
from kaleidoscope.globals import OptionType
from kaleidoscope.option_series import OptionSeries
from kaleidoscope.options.option_query import OptionQuery

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

DEBUG = True


class OptionStrategies(object):
    """
    Static methods to define option strategies
    """
    @staticmethod
    def generate_offsets(chain, width, shift_col, option_type):
        """
        :param chain: Dataframe to attach new offset columns to
        :param width: width of the spreads
        :param shift_col: the columns to apply shift
        :param option_type: the option type to construct spreads with
        :return: None
        """

        if DEBUG:
            chain.output_to_csv("offset_input_test_w_%s_%s" % (width, option_type.value[0].upper()))

        # TODO: Thoroughly test this algorithm for widths with .25, .5, 10, 50, etc increments
        # Calculate the distance of the strikes between each row width
        chain['dist'] = chain['strike'].shift(math.ceil(width) * -1 * option_type.value[1]) - chain['strike']

        # Calculate the factor between the distance and the specified width
        chain['factor'] = chain['dist'] / width

        # Using the specified width and factor, calculate the offset for each row
        chain['offset'] = -1 * width / chain['factor']
        chain['offset'] = chain['offset'].fillna(0)
        chain['offset'] = np.ceil(chain['offset']) if option_type == OptionType.PUT else np.floor(chain['offset'])

        # remove the unnecessary columns
        chain = chain.drop(['dist', 'factor'], axis=1)

        # get the unique offset values
        offsets = chain['offset'].value_counts(dropna=True).index.sort_values(ascending=False)
        # if there are more than one offset value, create a separate Dataframe for each offset amount
        chains = []

        for offset in offsets:
            chain_copy = chain.copy()
            for col in shift_col:
                new_col = col[0] + '_shifted'
                chain_copy[new_col] = chain[col[0]].shift(int(offset))
                chain_copy.dropna(inplace=True)

            # check distance equals specified width, trim distances that do not match the width
            chain_copy['dist_check'] = abs(chain_copy['strike_shifted'] - chain_copy['strike'])
            chain_copy = chain_copy[chain_copy['dist_check'] == float(width)]
            chain_copy.drop(['dist_check', 'offset'], axis=1, inplace=True)
            chains.append(chain_copy)

        concat_df = pd.concat(chains, ignore_index=True).sort_values('symbol', axis=0).reset_index(drop=True)

        if DEBUG:
            concat_df.output_to_csv("offset_results_test_w_%s_%s" % (width, option_type.value[0].upper()))

        return concat_df

    @staticmethod
    def moneyness(option_type, underlying, h_strike, l_strike):
        """
        Determine the moneyness of an option
        :param option_type: option type, 'c' or 'p'
        :param underlying: price of the underlying asset of option
        :param h_strike: higher strike of the spread
        :param l_strike: lower strike of the spread
        :return: distance between the higher strike and underlying if puts,
                 distance between the lower strike and underlying if calls
        """
        # TODO: may want to normalize option_type coming in from data source
        if (option_type == 'c' and underlying < l_strike) or (option_type == 'p' and underlying > h_strike):
            return "ITM"
        elif (option_type == 'c' and underlying > l_strike) or (option_type == 'p' and underlying < h_strike):
            return "OTM"
        elif (option_type == 'c' and underlying == l_strike) or (option_type == 'p' and underlying == h_strike):
            return "ATM"

    @staticmethod
    def vertical_spread(chain, width, option_type):
        """
        The vertical spread is an option spread strategy whereby the
        option trader purchases a certain number of options and simultaneously
        sell an equal number of options of the same class, same underlying security,
        same expiration date, but at a different strike price.

        :param chain: Filtered Dataframe to vertical spreads with.
        :param width: Distance in value between the strikes to construct vertical spreads with.
        :param option_type: The option type for this spread
        :return: A new dataframe containing all vertical spreads created from dataframe

        """

        # check that the width is allowed based
        strikes = chain['strike']

        shift_col = [(col[0], col[3]) for col in opt_params if col[2] == 1 and col[1] != -1]
        sc = OptionStrategies.generate_offsets(chain.copy(), width, shift_col, option_type)

        # calculate the spread's bid and ask prices
        for col in shift_col:
            # handle bid ask special case
            col_name = col[0]
            func = col[1]
            if col_name == 'bid':
                sc['spread_' + col_name] = func(sc[col_name], sc['ask_shifted'])
            elif col_name == 'ask':
                sc['spread_' + col_name] = func(sc[col_name], sc['bid_shifted'])
            else:
                if func is not None:
                    sc['spread_' + col_name] = func(sc[col_name], sc[col_name + '_shifted'])

        sc['spread_mark'] = (sc['spread_bid'] + sc['spread_ask']) / 2

        if option_type == OptionType.CALL:
            sc['spread_symbol'] = sc['symbol'] + "-." + sc['symbol_shifted']
        elif option_type == OptionType.PUT:
            sc['spread_symbol'] = sc['symbol_shifted'] + "-." + sc['symbol']

        sc.rename(columns={'strike': 'lower_strike'}, inplace=True)
        sc.rename(columns={'strike_shifted': 'higher_strike'}, inplace=True)

        # clean up the results, drop NaN
        sc = sc.dropna()

        sc = sc[['spread_symbol', 'quote_date', 'expiration', 'spread_mark',
                 'underlying_price', 'lower_strike', 'higher_strike']]

        return sc

    @staticmethod
    def iron_condor(chain, call_spread_width, put_spread_width):
        pass

    @staticmethod
    def custom(chain, **kwargs):
        pass


def construct(strategy, chains, **kwargs):
    """
    This is a convenience method to allow for creation of option spreads
    from predefined sources.

    :param strategy: The option strategy filter to use
    :param chains: Option chains data to use. This data should come from data.get() method
    :param kwargs: Parameters used to construct the spreads
    :return:
    """

    # process each quote date and pass option chain to strategy
    quote_list = []
    dates = sorted(chains.keys())

    for quote_date in dates:
        option_qy = OptionQuery(chains[quote_date])
        quote_list.append(strategy(quote_date, option_qy, **kwargs))

    # concatenate each day's dataframe containing the option chains
    spread_chains = pd.concat(quote_list, axis=0, ignore_index=True, copy=False)

    # assign the name of this concatenated dataframe to be the name of the strategy function
    spread_chains.name = strategy.__name__

    return OptionSeries(spread_chains)
