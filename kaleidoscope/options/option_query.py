"""
This class takes a dataframe of option chains and
returns a subset based on convenience methods provided
by this class to filter for specific option legs.
"""
import operator

import pandas as pd

from kaleidoscope.globals import Period, OptionType
from kaleidoscope.options.option_strategy import OptionStrategy


class OptionQuery(object):
    """
    The goal of this class is to abstract away dataframe manipulation
    functions and provide an easy to use interface to query for specific
    option legs in a dataframe. All functions will return a new pandas
    dataframe to allow for method chaining
    """

    def __init__(self, option_chain, inplace=False):
        # Create a copy of the option chain dataframe to prevent modifying
        # the original dataframe and to able to reuse it for other queries
        self.option_chain = option_chain.copy() if not inplace else option_chain
        self.option_chain.reset_index(drop=True, inplace=True)

        # create t_delta column if not present
        if 't_delta' not in self.option_chain.columns:
            # convert date columns to pandas datetime
            self.option_chain.loc[:, 'quote_date'] = pd.to_datetime(self.option_chain['quote_date'])
            self.option_chain.loc[:, 'expiration'] = pd.to_datetime(self.option_chain['expiration'])

            # calculate the difference between expiration date and quote date
            t_delta = self.option_chain['expiration'] - self.option_chain['quote_date']
            self.option_chain['t_delta'] = t_delta.dt.days

            # QUERY METHODS =================================================================================

    def puts(self):
        """
        Filter the class' copy of the option chain for put options
        """
        chain = self.option_chain
        chain = chain[chain.option_type.str.contains('p', case=False)]
        return OptionQuery(chain)

    def calls(self):
        """
        Filter the class' copy of the option chain for call options
        """
        chain = self.option_chain
        chain = chain[chain.option_type.str.contains('c', case=False)]
        return OptionQuery(chain)

    def option_type(self, option_type):
        """
        Filter the class' copy of the option chain for specified option type
        """

        if isinstance(option_type, OptionType):
            chain = self.option_chain
            chain = chain[chain.option_type.str.contains(option_type.value[0], case=False)]
            return OptionQuery(chain)
        else:
            raise ValueError("option_type must be of type OptionType")

    def nearest(self, column, val, tie='roundup'):
        """
        Returns a dataframe row containing the column item nearest to the
        given value.

        :param column: column to look up value
        :param val: return values nearest to this param
        :return: A new OptionQuery object with filtered dataframe

        """
        keyval = self._convert(column, val)

        self.option_chain['abs_dist'] = abs(self.option_chain[keyval[0]] - keyval[1])
        min_abs_dist = self.option_chain['abs_dist'].min()

        filtered_df = self._compare('abs_dist', operator.eq, min_abs_dist)
        filtered_df = filtered_df.drop(['abs_dist'], axis=1)

        if len(filtered_df) != 1:
            if tie == 'roundup':
                filtered_df = filtered_df[filtered_df[column] == filtered_df[column].max()]
            elif tie == 'rounddown':
                filtered_df = filtered_df[filtered_df[column] == filtered_df[column].min()]

        return OptionQuery(filtered_df)

    def offset(self, column, offset_from, offset, mode='pct'):
        """
        Returns the dataframe rows where the column value are at an offset
        to the value provided to this function
        """
        offset = self._offset(offset_from, offset, mode)
        return self.nearest(column, offset)

    def lte(self, column, val):
        """
        Returns a dataframe with rows where column values are less than or
        equals to the val parameter

        :param column: column to look up value
        :param val: return values less than or equals to this param
        :return: A new OptionQuery object with filtered dataframe
        """
        keyval = self._convert(column, val)
        return OptionQuery(self._compare(keyval[0], operator.le, keyval[1]))

    def gte(self, column, val):
        """
        Returns a dataframe with rows where column values are greater than or
        equals to the val parameter

        :param column: column to look up value
        :param val: return values greater than or equals to this param
        :return: A new OptionQuery object with filtered dataframe
        """
        keyval = self._convert(column, val)
        return OptionQuery(self._compare(keyval[0], operator.ge, keyval[1]))

    def eq(self, column, val):
        """
        Returns a dataframe with rows where column values are
        equal to this param.

        :param column: column to look up value
        :param val: return values equals to this param amount
        :return: A new OptionQuery object with filtered dataframe
        """
        keyval = self._convert(column, val)
        return OptionQuery(self._compare(keyval[0], operator.eq, keyval[1]))

    def lt(self, column, val):
        """
        Returns a dataframe with rows where column values are
        equal to this param.

        :param column: column to look up value
        :param val: return values less than this param amount
        :return: A new OptionQuery object with filtered dataframe
        """
        keyval = self._convert(column, val)
        return OptionQuery(self._compare(keyval[0], operator.lt, keyval[1]))

    def gt(self, column, val):
        """
        Returns a dataframe with rows where column values are
        equal to this param.

        :param column: column to look up value
        :param val: return values greater than this param amount
        :return: A new OptionQuery object with filtered dataframe
        """
        keyval = self._convert(column, val)
        return OptionQuery(self._compare(keyval[0], operator.gt, keyval[1]))

    def ne(self, column, val):
        """
        Returns a dataframe with rows where column values are
        equal to this param.

        :param column: column to look up value
        :param val: return values not equal to this param amount
        :return: A new OptionQuery object with filtered dataframe
        """
        keyval = self._convert(column, val)
        return OptionQuery(self._compare(keyval[0], operator.ne, keyval[1]))

    def min(self, column):
        """
        Return the row with the min value of the specified column
        :param column: column to look up min value
        :return: Series object containing row with min value of column
        """

        # TODO: check this works on a date field
        idx_min = self.option_chain[column].idxmin()
        return self.option_chain.iloc[idx_min]

    def max(self, column):
        """
        Return the row with the max value of the specified column
        :param column: column to look up min value
        :return: Series object containing row with max value of column
        """

        # TODO: check this works on a date field
        idx_max = self.option_chain[column].idxmax()
        return self.option_chain.iloc[idx_max]

    # GET METHODS ===================================================================================

    def get(self, column):
        """
        Returns the specified column's unique values in an array
        """
        return self.option_chain[column].unique()

    def get_offset(self, offset_from, offset, mode='pct'):
        """
        Get the offset value based on the params
        :param offset_from: the value to calculate offset from
        :param offset: the offset amount based on mode selected
        :param mode: the method to calculate the offset amount.
                     modes: pct (percent), step (strike steps), val (value amount)
        :return: amount resulting from the offset
        """
        return self._offset(offset_from, offset, mode)

    def get_underlying_price(self):
        """
        Gets the underlying price info from the option chain if available
        :return: The average of all underlying prices that may have been
                 recorded in the option chain for a given day.
        """
        if 'underlying_price' in self.option_chain.columns:
            dates = self.option_chain['underlying_price'].unique()
            return dates.mean()
        else:
            return OptionQuery(self.option_chain)

    # PRIVATE METHODS ===============================================================================

    def _convert(self, column, val):
        """
        In the use case where column and val are datetime and Period instances, respectively,
        change the column lookup to lookup 't_delta' column and get the actual Period value from
        Period object.

        :param column: datetime column to lookup
        :param val: an Enum instance of Period
        :return: tuple of lookup column and val (converted if needed)
        """
        lookup_col = column

        if self.option_chain[column].dtype == 'datetime64[ns]' and isinstance(val, Period):
            val = val.value
            lookup_col = 't_delta'
        else:
            val = float(val)

        return lookup_col, val

    def _strip(self):
        """
        Remove unnecessary columns, used for final output of fetch functions
        """
        return self.option_chain.drop(['t_delta'], axis=1)

    def _compare(self, column, op, val):
        """
        Compares the column value to the val param using the operator passed in op param

        :param column: column to compare with
        :param op: operator to use for comparison, this is a Python Operator object
        :param val: value to compare with
        :return: The filtered option chain that matches the comparison criteria
        """
        return self.option_chain[op(self.option_chain[column], val)]

    def _offset(self, offset_from, offset, mode):
        """
        Returns the offset value based on the option chain

        :param offset_from: The value to apply offset from
        :param offset: The amount to offset from the offset_from value
        :param mode: Defaults to a percentage offset. If 'step' offset value
                     represents the number of strikes to offset.
        :return: Value as a result of the specified offset
        """

        if mode == 'pct':
            offset = offset_from + (offset_from * offset)
        elif mode == 'step':  # TODO: implement
            pass
        elif mode == 'val':
            offset = offset_from + offset

        return offset

    # OUTPUT METHODS =================================================================================

    def fetch(self):
        """
        Return all rows of this object's option chain
        """
        return self._strip()

    def to_strat(self):
        """
        Return an OptionStrategy object created from the filtered option chains
        :return: OptionStrategy
        """
        if self.option_chain.shape[0] > 1:
            raise ValueError("Option chains cannot be more than one row")
        else:
            return OptionStrategy(self.option_chain)

    # OPTION STRATEGY METHODS ========================================================================

    def verticals(self, width, option_type, dte=None):
        """
        The vertical spread is an option spread strategy whereby the
        option trader purchases a certain number of options and simultaneously
        sell an equal number of options of the same class, same underlying security,
        same expiration date, but at a different strike price.

        :param width: Distance in value between the strikes to construct vertical spreads with.
        :param option_type: The option type for this spread
        :param dte: Date to expiration
        :return: A new dataframe containing all vertical spreads created from dataframe
        """

        if width <= 0:
            raise ValueError("Width of vertical spreads cannot be less than or equal 0")

        chains = self.option_type(option_type)
        chains = chains.lte('expiration', dte).fetch() if dte is not None else chains.fetch()

        # shift only the strikes since this is a vertical spread
        chains['strike_key'] = chains['strike'] + (width * option_type.value[1])
        left_keys = ['quote_date', 'expiration', 'root', 'option_type', 'strike_key']
        right_keys = ['quote_date', 'expiration', 'root', 'option_type', 'strike']

        chains = chains.merge(chains, left_on=left_keys, right_on=right_keys, suffixes=('', '_shifted'))

        chains['strategy'] = 'Vertical'
        chains['symbol'] = '.' + chains['symbol'] + '-.' + chains['symbol_shifted']
        chains['mark'] = ((chains['bid'] - chains['ask_shifted']) + (chains['ask'] - chains['bid_shifted'])) / 2
        chains['volume'] = chains['trade_volume'] + chains['trade_volume_shifted']
        chains = chains.rename(index=str, columns={"strike": "long_strike", "strike_shifted": "short_strike"})

        cols = ['symbol', 'strategy', 'underlying_symbol', 'quote_date', 'expiration',
                'volume', 'mark', 'long_strike', 'short_strike']

        for greek in ['delta', 'theta', 'gamma', 'vega', 'rho']:
            if greek in chains.columns:
                chains[greek] = chains[greek] - chains[greek + "_shifted"]
                cols.append(greek)

        return OptionQuery(chains[cols])
