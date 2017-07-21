from datetime import timedelta

import pandas as pd

from kaleidoscope.globals import OptionType, Period
from kaleidoscope.options.option_query import OptionQuery
from kaleidoscope.options.option_series import OptionSeries

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class OptionStrategies(object):
    """
    Static methods to define option strategies
    """

    @staticmethod
    def single(chain, **params):

        if 'option_type' not in params:
            raise ValueError("Must provide option_type for single option")

        # set the attributes for this option strategy
        OptionStrategies.single.option_config = {'option': 1}

        chains = OptionQuery(chain).option_type(params['option_type'])
        chains = chains.lte('expiration', params['DTE']).fetch() if 'DTE' in params else chains.fetch()

        return chains

    @staticmethod
    def vertical(chain, **params):
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

        if 'option_type' not in params or 'width' not in params:
            raise ValueError("Must provide option_type and width parameters for vertical spreads")
        elif params['width'] <= 0:
            raise ValueError("Width of vertical spreads cannot be less than or equal 0")

        chains = OptionQuery(chain).option_type(params['option_type'])
        chains = chains.lte('expiration', params['DTE']).fetch() if 'DTE' in params else chains.fetch()

        # shift only the strikes since this is a vertical spread
        chains['strike_key'] = chains['strike'] + (params['width'] * params['option_type'].value[1])
        left_keys = ['quote_date', 'expiration', 'root', 'option_type', 'strike_key']
        right_keys = ['quote_date', 'expiration', 'root', 'option_type', 'strike']

        chains = chains.merge(chains, left_on=left_keys, right_on=right_keys, suffixes=('', '_shifted'))

        return OptionQuery(chains)

    @staticmethod
    def iron_condor(chain, **params):
        """
        The iron condor is an option trading strategy utilizing two vertical spreads
        – a put spread and a call spread with the same expiration and four different strikes.
        A long iron condor is essentially selling both sides of the underlying instrument by
        simultaneously shorting the same number of calls and puts, then covering each position
        with the purchase of further out of the money call(s) and put(s) respectively.
        The converse produces a short iron condor.

        :param chain: Filtered Dataframe to vertical spreads with.
        :param width: Width between the middle strikes.
        :param c_width: Width of the call spreads
        :param p_width: Width of the put spreads
        :return: A new dataframe containing all iron condors created from dataframe
        """

        if 'c_width' not in params or 'p_width' not in params or 'width' not in params:
            raise ValueError("Must define all widths for iron condor")

        call_side = OptionStrategies.vertical(chain, width=params['c_width'], option_type=OptionType.CALL).fetch()
        put_side = OptionStrategies.vertical(chain, width=params['p_width'], option_type=OptionType.PUT).fetch()
        put_side['strike_key'] = put_side['strike'] + params['width']

        call_side_keys = ['quote_date', 'expiration', 'root', 'strike']
        put_side_keys = ['quote_date', 'expiration', 'root', 'strike_key']

        chains = call_side.merge(put_side, left_on=call_side_keys, right_on=put_side_keys, suffixes=('_c', '_p'))

        return OptionQuery(chains)

    @staticmethod
    def covered_stock(chain, **params):
        """
        A covered call is an options strategy whereby an investor holds a long position
        n an asset and writes (sells) call options on that same asset in an attempt to
        generate increased income from the asset.

        Writing covered puts is a bearish options trading strategy involving the
        writing of put options while shorting the obligated shares of the underlying stock.

        :param chain: Filtered Dataframe to vertical spreads with.
        :param option_type: The option type for this spread
        :return: A new dataframe containing all covered stock created from dataframe
        """

        if 'option_type' not in params:
            raise ValueError("Must provide option_type for covered stock")

        # set the attributes for this option strategy
        OptionStrategies.covered_stock.option_config = {'stock': 100, 'option': 1}

        out_col = OptionStrategies.base_out_col

        chains = OptionQuery(chain).option_type(params['option_type'])
        chains = chains.lte('expiration', params['DTE']).fetch() if 'DTE' in params else chains.fetch()

        side = -1 * params['option_type'].value[1]

        chains['spread_mark'] = (side * (chains['bid'] + chains['ask']) / 2) + chains['underlying_price']

        prefix = "-." if params['option_type'] == OptionType.CALL else "."
        chains['spread_symbol'] = prefix + chains['symbol'] + "+100*" + chains['underlying_symbol']

        return chains[out_col + ['strike']]

    @staticmethod
    def diagonal(chain, **params):
        pass

    @staticmethod
    def double_diagonal(chain, **params):
        pass

    @staticmethod
    def calendar(chain, **params):
        """
        A calendar spread is a strategy involving buying longer term options and selling 
        equal number of shorter term options of the same underlying stock or index with the 
        same strike price. Calendar spreads can be done with calls or with puts, 
        which are virtually equivalent if using same strikes and expirations.
        
        They can use ATM (At The Money) strikes which make the trade neutral.
        If using OTM (Out Of The Money) or ITM (In The Money) strikes, 
        the trade becomes directionally biased.

        :param chain: Filtered Dataframe to vertical spreads with.
        :param option_type: The option type for this spread
        :param depth: The period to represent the difference between the expiration dates of the two options
        :return: A new dataframe containing all covered stock created from dataframe
        """
        if 'option_type' not in params:
            raise ValueError("Must provide option_type for calendar spread")
        elif 'depth' not in params:
            raise ValueError("Must provide period depth for calender spread")

        # set the attributes for this option strategy
        OptionStrategies.calendar.option_config = {'option': 2}

        out_col = OptionStrategies.base_out_col
        shift = Period.ONE_WEEK if 'depth' not in params else params['depth']

        chains = OptionQuery(chain).option_type(params['option_type'])
        chains = chains.lte('expiration', params['DTE']).fetch() if 'DTE' in params else chains.fetch()
        # create column with expiration shifted by depth
        chains['expiration_key'] = chains['expiration'] + timedelta(days=shift.value)

        left_keys = ['quote_date', 'expiration_key', 'option_type', 'strike']
        right_keys = ['quote_date', 'expiration', 'option_type', 'strike']

        chains = chains.merge(chains, left_on=left_keys, right_on=right_keys, suffixes=('', '_shifted'))

        if chains.empty:
            raise ValueError("Cannot construct calendar spreads. Check expirations exists for specified depth.")

        # calculate the spread's bid and ask prices
        for c, f in OptionStrategies.shift_col:
            # handle bid ask special case
            if c == 'bid':
                chains['spread_' + c] = f(chains[c], chains['ask_shifted'])
            elif c == 'ask':
                chains['spread_' + c] = f(chains[c], chains['bid_shifted'])
            else:
                if f is not None:
                    chains['spread_' + c] = f(chains[c], chains[c + '_shifted'])

        chains['spread_mark'] = (chains['spread_bid'] + chains['spread_ask']) / 2
        chains['spread_symbol'] = "." + chains['symbol_shifted'] + "-." + chains['symbol']

        # assign the strategy name to this dataframe's name attribute
        chains.name = OptionStrategies.single.__name__

        return chains[out_col + ['strike', 'expiration_shifted']]

    @staticmethod
    def straddle(chain, **params):
        pass

    @staticmethod
    def strangle(chain, **params):
        pass

    @staticmethod
    def combo(chain, **params):
        pass

    @staticmethod
    def back_ratio(chain, **params):
        pass

    @staticmethod
    def butterfly(chain, **params):
        pass

    @staticmethod
    def condor(chain, **params):
        pass

    @staticmethod
    def custom(chain, **params):
        pass


def construct(symbol, strategy, chains, **kwargs):
    """
    This is a convenience method to allow for creation of option spreads
    from predefined sources.

    :param symbol: The symbol of the option chains
    :param strategy: The option strategy filter to use
    :param chains: Option chains data to use. This data should come from data.get() method
    :param kwargs: Parameters used to construct the spreads
    :return:
    """

    # wrap dataframes into OptionSeries object to be used in backtest
    spread_chains = strategy(chains, **kwargs)
    return OptionSeries(symbol, strategy.__name__, spread_chains, **kwargs)
