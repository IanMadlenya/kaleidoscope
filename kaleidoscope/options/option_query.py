"""
This class takes a dataframe of option chains and
returns a subset based on convenience methods provided
by this class to filter for specific option legs.
"""
import pandas as pd
import operator
from kaleidoscope.globals import Period

class OptionQuery(object):
    """
    The goal of this class is to abstract away dataframe manipulation
    functions and provide an easy to use interface to query for specific
    option legs in a dataframe. All functions will return a new pandas
    dataframe to allow for method chaining
    """

    def __init__(self, option_chain):
        # Create a copy of the option chain dataframe to prevent modifying
        # the original dataframe and to able to reuse it for other queries
        self.option_chain = option_chain.copy()

        # create t_delta column if not present
        if 't_delta' not in self.option_chain.columns:
            # convert date columns to pandas datetime
            self.option_chain['quote_date'] = pd.to_datetime(self.option_chain['quote_date'])
            self.option_chain['expiration'] = pd.to_datetime(self.option_chain['expiration'])

            # calculate the difference between expiration date and quote date
            t_delta = self.option_chain['expiration'] - self.option_chain['quote_date']
            self.option_chain['t_delta'] = t_delta.dt.days

# QUERY METHODS =================================================================================

    def put(self):
        """
        Filter the class' copy of the option chain for put options
        """
        chain = self.option_chain
        chain = chain[chain.option_type.str.contains('p', case=False)]
        return OptionQuery(chain)

    def call(self):
        """
        Filter the class' copy of the option chain for call options
        """
        chain = self.option_chain
        chain = chain[chain.option_type.str.contains('c', case=False)]
        return OptionQuery(chain)

    def closest(self, column, val):
        """
        Returns a dataframe row containing the column item closest to the
        given value.

        :param column: column to look up value
        :param val: return values closest to this param
        :return: A new OptionQuery object with filtered dataframe

        """
        keyval = self._convert(column, val)
        abs_dist = (self.option_chain[keyval[0]] - keyval[1]).abs()

        return OptionQuery(self._compare(abs_dist, operator.eq, abs_dist.min()))

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

    def bracket(self, strike, width, pct=True, pos='mid'):
        """
        Returns the dataframe rows containing the column values
        that are above and below the strike price

        :param strike:
        :param width:
        :param pct:
        :param pos:
        :return:
        """
        pass

    def offset(self, column, val, width, mode='pct'):
        """
        Returns the dataframe rows where the column value are at an offset
        to the value provided to this function
        """
        offset = self._offset(column, val, width, mode)
        return self.closest(column, offset)

# GET METHODS ===================================================================================

    def get(self, column):
        """
        Returns the specified column's unique values in an array
        """
        return self.option_chain[column].unique()

    def get_closest(self, column, val):
        """
        Returns the column item value closest to the given value
        """
        chain = self._closest(column, val)
        return chain[column].iloc[0]

    def get_bracket(self, strike, width, pct=True, pos='mid'):
        """
        Returns the column values that are above and below the strike price
        """
        pass

    def get_offset(self, column, val, width, mode='pct'):
        """
        Returns the offset value based on the option chain
        """
        offset = self._offset(column, val, width, mode)
        return self.get_closest(column, offset)

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

        return (lookup_col, val)

    def _strip(self):
        """
        Remove unnessesary columns, used for final output of fetch functions
        """
        return self.option_chain.drop('t_delta', axis=1)

    def _compare(self, column, op, val):
        """
        Compares the column value to the val param using the operator passed in op param

        :param column: column to compare with
        :param op: operator to use for comparison, this is a Python Operator object
        :param val: value to compare with
        :return: The filtered option chain that matches the comparison criteria
        """
        return self.option_chain[op(self.option_chain[column], val)]

    def _bracket(self, strike, width, mode='pct', pos='mid'):
        """
        Returns a tuple containing the values that are above, below and the strike price

        params:

        strike: strike value to base the 'pos' parameter from.
        dist: the distance in either direction for the top and bottom option legs
        mode: 'pct' (default) - the distance of the strike is the percentage of the
                                param value.
              'strikes'       - the distance of the strike is the number of strikes
                                above and/or below the strike price
              'val'           - the distance of the strike is the strike plus or minus
                                the width amount in value
        pos: 'mid' (default)  - the strike price will be between the top and bottom leg
             'upper'           - the strike price will be the higher priced leg
             'lower'            - the strike price will be the lower priced leg
        """

        upper_strike = None
        lower_strike = None

        if mode == 'pct':
            if pos == 'lower':
                upper_strike = strike + (strike * width)
                lower_strike = strike
            elif pos == 'mid':
                upper_strike = strike + (strike * width / 2)
                lower_strike = strike - (strike * width / 2)
            elif pos == 'upper':
                upper_strike = strike
                lower_strike = strike - (strike * width)
        elif mode == 'strikes':
            if pos == 'lower':
                upper_strike = None
                lower_strike = None
            elif pos == 'mid':
                upper_strike = None
                lower_strike = None
            elif pos == 'upper':
                upper_strike = None
                lower_strike = None
        elif mode == 'val':
            if pos == 'lower':
                upper_strike = strike + width
                lower_strike = strike
            elif pos == 'mid':
                upper_strike = strike + width
                lower_strike = strike - width
            elif pos == 'upper':
                upper_strike = strike
                lower_strike = strike - width

        return (upper_strike, lower_strike, strike)

    def _offset(self, column, val, width, mode):
        """
        Returns the offset value based on the option chain
        """

        if mode == 'pct':
            offset = val + (val * width)
        elif mode == 'step': # TODO: implement
            # isolate all the unique values of the selected column
            col = self.option_chain[column].unique()
            # get the closest value to the column of the provided val
            col_val = self.get_closest(column, val)

        elif mode == 'val':
            offset = val + width

        return offset

# FETCH METHODS =================================================================================

    def fetch(self):
        """
        Return all rows of this object's option chain
        """
        return self._strip()

    def fetch_first(self):
        """
        Return the first row of this object's option chain. Will be the lowest
        strike price of the chain
        """
        return self._strip().head(1)

    def fetch_last(self):
        """
        Return the last row of this object's option chain. Will be the highest
        strike price of the chain
        """
        return self._strip().tail(1)





    