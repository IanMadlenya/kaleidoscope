"""
module doc string
"""

import datetime
import os
import sqlite3

import pandas as pd

import kaleidoscope.globals as gb
from kaleidoscope.options.option_query import OptionQuery

# map columns from data source to the standard option columns used in the library
opt_params = (
    ('symbol', 0),
    ('underlying_symbol', -1),
    ('quote_date', 2),
    ('root', -1),
    ('expiration', 4),
    ('strike', 5),
    ('option_type', 6),
    ('open', -1),
    ('high', -1),
    ('low', -1),
    ('close', -1),
    ('trade_volume', 11),
    ('bid_size', -1),
    ('bid', 13),
    ('ask_size', -1),
    ('ask', 15),
    ('underlying_price', 16),
    ('iv', -1),
    ('delta', -1),
    ('gamma', -1),
    ('theta', -1),
    ('vega', -1),
    ('rho', -1),
    ('open_interest', -1)
)


def get(ticker, start, end, option_filter,
        filter_params=None, provider=None, path=None,
        exclude_splits=True, option_type=None):
    """
    Helper function for retrieving data as a DataFrame.

    :param ticker: the symbol to download
    :param start: expiration start date of downloaded data
    :param end: expiration end date of downloaded data
    :param option_filter: the option strategy to construct with the data source
    :param filter_params: the parameters to pass into the option strategy on initialization
    :param provider: The data source to use for downloading data, reference to function
                     Defaults to sqlite database
    :param path: Path to the data source
    :param exclude_splits: Should data exclude options created from the underlying's stock splits
    :param option_type: If None, or not passed in, will retrieve both calls and puts of option chain
    :return: Dataframe containing all option chains as filtered by algo for the specified date range
    """

    provider_kwargs = {}

    # default to sqlite provider if none specified
    if provider is None:
        provider = sqlite

    # exclude option chains created from the underlying's stock split
    if exclude_splits:
        provider_kwargs['root'] = ticker

    if option_type == 'c':
        provider_kwargs['option_type'] = 'c'

    if option_type == 'p':
        provider_kwargs['option_type'] = 'p'

    # Providers will return an dictionary where quote_dates is key,
    # and DataFrames of option chains for that date as value
    option_chains = provider(ticker, start, end, path, provider_kwargs)

    # process each quote date and pass option chain to pattern
    quote_list = []
    dates = sorted(option_chains.keys())

    for quote_date in dates:
        sliced_chains = _slice(quote_date, option_chains)
        quote_list.append(option_filter(quote_date, sliced_chains, filter_params))

    # concatenate each day's dataframe containing the option chains
    test_chains = pd.concat(quote_list, axis=0, ignore_index=True, copy=False)

    # assign the name of this concatenated dataframe to be the name of the strategy function
    test_chains.name = option_filter.__name__

    return test_chains


def sqlite(ticker, start, end, path=None, params=None):
    """
    Data provider wrapper around pandas read_sql_query for sqlite database.

    :param ticker: Ticker to download option data for
    :param path: full path to data file
    :param start: start date to retrieve data from
    :param end: end date to retrieve data to
    :param params: specific params used in query to retrieve data
    :return:
    """

    if path is None:
        # use default path if no path given
        path = os.path.join(os.sep, gb.PROJECT_DIR, gb.DATA_SUB_DIR, gb.FILE_NAME + ".db")

    try:
        data_conn = sqlite3.connect(path)

        # Build the default query
        query = f"SELECT * FROM {ticker}_option_chain WHERE expiration >= '{start}' AND expiration <= '{end}'"

        # loop through opt_params, assign filter by column if applicable
        if params is not None:
            query += " AND"
            for k, v in params.items():
                query += f" {k} = '{v}' AND"

            # remove the trailing 'AND'
            query = query[:-4]

        # may need to apply chunk size if loading large option chain set
        data = pd.read_sql_query(query, data_conn)

        # normalize dataframe columns
        data = _normalize(data)
        unique_quote_dates = data['quote_date'].unique()
        option_chains = {elem: pd.DataFrame for elem in unique_quote_dates}

        # populate the dictionary
        for key in option_chains.keys():
            option_chains[key] = data[:][data["quote_date"] == key]

        return option_chains

    except IOError as err:
        print("Database Connection Error: ", err)


def output_to_csv(prices):
    """
    Thin wrapper method to output this dataframe to csv file
    :param prices: This is the dataframe itself
    :return:
    """
    filename = '%s_%s' % (prices.name, datetime.date.today())
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


def _slice(date, chains):
    """
    Return the option chain dataframe for the parameter date

    :param date: the date to lookup option chains for
    :return: the dataframe containing the option chain for the param date,
             otherwise, return None
    """

    if date in chains:
        option_qy = OptionQuery(chains[date])
        chains[date] = option_qy
        return chains[date]

    return None
