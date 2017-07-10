import datetime
import operator as op
import os
import sqlite3

import pandas as pd

import kaleidoscope.globals as gb

# map columns from data source to the standard option columns used in the library.
# first position of tuple: column names used in program
# second position of tuple: column index of the source data that maps to the column in this program
#                           -1 means do not map this column
# third position of tuple: 0 if this column should not be shifted when constructing a spread, 1 means
#                          the column value should be merged during spread construction.


opt_params = (
    ('symbol', 0, 1, None),
    ('underlying_symbol', -1, 0, None),
    ('quote_date', 2, 0, None),
    ('root', -1, 0, None),
    ('expiration', 4, 0, None),
    ('strike', 5, 1, None),
    ('option_type', 6, 0, None),
    ('open', -1, 0, None),
    ('high', -1, 0, None),
    ('low', -1, 0, None),
    ('close', -1, 0, None),
    ('trade_volume', 11, 1, op.add),
    ('bid_size', -1, 1, op.add),
    ('bid', 13, 1, op.sub),
    ('ask_size', -1, 1, op.add),
    ('ask', 15, 1, op.sub),
    ('underlying_price', 16, 0, None),
    ('iv', -1, 1, None),
    ('delta', -1, 1, op.sub),
    ('gamma', -1, 1, op.sub),
    ('theta', -1, 1, op.sub),
    ('vega', -1, 1, op.sub),
    ('rho', -1, 1, op.sub),
    ('open_interest', -1, 1, op.add)
)


def get(ticker, start, end,
        provider=None, path=None,
        include_splits=False, option_type=None):
    """
    Helper function for retrieving data as a DataFrame.

    :param ticker: the symbol to download
    :param start: expiration start date of downloaded data
    :param end: expiration end date of downloaded data
    :param provider: The data source to use for downloading data, reference to function
                     Defaults to sqlite database
    :param path: Path to the data source
    :param include_splits: Should data exclude options created from the underlying's stock splits
    :param option_type: If None, or not passed in, will retrieve both calls and puts of option chain
    :return: Dataframe containing all option chains as filtered by algo for the specified date range
    """

    if provider is None:
        provider = sqlite

    # TODO: check that the query returned data
    # Providers will return an dictionary where quote_dates is key,
    # and DataFrames of option chains for that date as value
    return provider(ticker, start, end, path, include_splits, option_type)


def sqlite(ticker, start, end, path=None,
           include_splits=False, option_type=None):
    """
    Data provider wrapper around pandas read_sql_query for sqlite database.

    :param ticker: Ticker to download option data for
    :param path: full path to data file
    :param start: start date to retrieve data from
    :param end: end date to retrieve data to
    :return: Dictionary with quote_date as key, dataframe containinginin option chains as value
    """
    # TODO: allow for various start and end date configurations

    params = {}

    # exclude option chains created from the underlying's stock split
    if not include_splits:
        params['root'] = ticker

    if option_type == 'c':
        params['option_type'] = 'c'

    if option_type == 'p':
        params['option_type'] = 'p'

    if path is None:
        # use default path if no path given
        path = os.path.join(os.sep, gb.PROJECT_DIR, gb.DATA_SUB_DIR, gb.DB_NAME + ".db")

    try:
        data_conn = sqlite3.connect(path)

        # Build the default query
        query = "SELECT * FROM %s_option_chain WHERE expiration >= '%s' AND expiration <= '%s'" % (ticker, start, end)

        # loop through opt_params, assign filter by column if applicable
        if params is not None:
            query += " AND"
            for k, v in params.items():
                query += " %s = '%s' AND" % (k, v)

            # remove the trailing 'AND'
            query = query[:-4]

        # may need to apply chunk size if loading large option chain set
        data = pd.read_sql_query(query, data_conn)

        # normalize dataframe columns
        data = _normalize(data)
        return data

    except IOError as err:
        print("Database Connection Error: ", err)


def output_to_csv(prices, name):
    """
    Thin wrapper method to output this dataframe to csv file
    :param prices: This is the dataframe itself
    :return:
    """

    filename = prices.name if hasattr(prices, name) else name
    csv_dir = os.path.join(os.sep, gb.PROJECT_DIR, gb.OUTPUT_DIR, filename + ".csv")
    prices.to_csv(csv_dir)


def _normalize(dataframe):
    """
    Normalize column names using opt_params defined in this class. Normalization
    means to map columns from data source that may have different names for the same
    columns to a standard column name that will be used in this program.

    :param dataframe: the pandas dataframe containing data from the data source
    :return: dataframe with the columns renamed with standard column names and unnecessary
             (mapped with -1) columns dropped
    """
    columns = list()
    col_names = list()

    for col in opt_params:
        if col[1] != -1:
            columns.append(col[1])
            col_names.append(col[0])

    dataframe = dataframe.iloc[:, columns]
    dataframe.columns = col_names

    return dataframe

