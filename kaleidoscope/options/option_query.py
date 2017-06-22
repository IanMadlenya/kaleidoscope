"""
This class takes a dataframe of option chains and
returns a subset based on convenience methods provided
by this class to filter for specific option legs.
"""
import operator

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
        given value.

        :param column: column to look up value
        :param val: return values closest to this param
        :return: A new OptionQuery object with filtered dataframe

        """
        keyval = self._convert(column, val)

        # TODO: may need to create an absolute distance col in dataframe
        abs_dist = (self.option_chain[keyval[0]] - keyval[1]).abs()
        # abs_dist = abs(self.option_chain[keyval[0]] - keyval[1])

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
        keyval = self._convert(column, val)
        abs_dist = (self.option_chain[keyval[0]] - keyval[1]).abs()

        chain = self._compare(abs_dist, operator.eq, abs_dist.min())
        return chain[keyval[0]].iloc[0]

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

    # FETCH METHODS =================================================================================

    def fetch(self):
        """
        Return all rows of this object's option chain
        """
        return self._strip()
