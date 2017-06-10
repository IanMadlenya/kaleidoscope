"""
This class takes a dataframe of option chains and
returns a subset based on convenience methods provided
by this class to filter for specific option legs.
"""
import pandas as pd
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
        given value
        """
        return OptionQuery(self._closest(column, val))

    def bracket(self, strike, width, pct=True, pos='mid'):
        """
        Returns the dataframe rows containing the column values
        that are above and below the strike price
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

    def _strip(self):
        """
        Remove unnessesary columns, used for final output of fetch functions
        """
        return self.option_chain.drop(['quote_date', 't_delta'], axis=1)

    def _closest(self, column, val):
        """
        Returns the column item value closest to the lookup value
        """
        chain = self.option_chain
        lookup_col = column

        if chain[lookup_col].dtype == 'datetime64[ns]' and isinstance(val, Period):
            val = val.value
            lookup_col = 't_delta'
        else:
            val = float(val)

        abs_dist = (chain[lookup_col]-val).abs()
        return chain[abs_dist == abs_dist.min()]

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
        strikes = self.option_chain['strikes'].unique()

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







    