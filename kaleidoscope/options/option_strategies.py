import math

import numpy as np
import pandas as pd

from kaleidoscope.datas import opt_params
from kaleidoscope.option_series import OptionSeries
from kaleidoscope.options.option_query import OptionQuery
from kaleidoscope.globals import Period, OptionType

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class OptionStrategies(object):
    """
    Static methods to define option strategies
    """

    shift_col = [(col[0], col[3]) for col in opt_params if col[2] == 1 and col[1] != -1]

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
        chains = chain.copy()

        # shift only the strikes since this is a vertical spread
        chains['strike_key'] = chains['strike'] + (width * option_type.value[1])

        chains = chains.merge(chains,
                              left_on=['quote_date', 'expiration', 'strike_key'],
                              right_on=['quote_date', 'expiration', 'strike'],
                              suffixes=('', '_shifted')
                              )

        chains = chains.drop(['strike_key', 'strike_key_shifted',
                              'option_type_shifted', 'underlying_price_shifted'], axis=1)
        
        # calculate the spread's bid and ask prices
        for col in OptionStrategies.shift_col:
            # handle bid ask special case
            col_name = col[0]
            func = col[1]
            if col_name == 'bid':
                chains['spread_' + col_name] = func(chains[col_name], chains['ask_shifted'])
            elif col_name == 'ask':
                chains['spread_' + col_name] = func(chains[col_name], chains['bid_shifted'])
            else:
                if func is not None:
                    chains['spread_' + col_name] = func(chains[col_name], chains[col_name + '_shifted'])

        chains['spread_mark'] = (chains['spread_bid'] + chains['spread_ask']) / 2
        chains['spread_symbol'] = chains['symbol'] + "-." + chains['symbol_shifted']

        chains = chains[['spread_symbol', 'quote_date', 'expiration', 'spread_mark',
                         'underlying_price', 'strike', 'strike_shifted']]

        return chains

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

    params = {
        'width': 2,
        'DTE': Period.SEVEN_WEEKS,
        'option_type': OptionType.CALL
    }

    params.update(kwargs)

    # pre-filter the options to create the option spread with
    chains = (OptionQuery(chains).lte('expiration', params['DTE'])
              .option_type(params['option_type'])
              .fetch()
              )

    # Batch create vertical call spreads on all strikes
    spread_chains = strategy(chains, width=params['width'], option_type=params['option_type'])

    # assign the name of this concatenated dataframe to be the name of the strategy function
    spread_chains.name = strategy.__name__

    return OptionSeries(spread_chains)
