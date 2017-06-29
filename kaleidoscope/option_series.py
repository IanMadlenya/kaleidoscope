import pandas as pd

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', None)


class OptionSeries(object):
    """
    This class contains the time series data for an option strategy.
    """

    def __init__(self, data, index=None, dropna=False):
        """
        Initialize this class with a dataframe of option strategy prices by
        symbol, quote date, expiration, mark, other metrics, etc

        This class will then store the data in a dictionary by expiration dates
        and provide methods that will act on this data.

        :param data: Dataframe containing the time series data of an option strategy.
                     This dataframe must contain the following columns:
                     symbol, quote_date, expiration, mark
        :param index: A list containing the index position for the 4 columns listed above,
                      if the columns are not listed in that order in the DataFrame.
                      If None, this function will infer the columns by the default order
        :param dropna: Drop all rows containing NaN in OptionSeries
        """

        # TODO: check index param's length is equal to 4
        if not isinstance(data, pd.DataFrame):
            raise ValueError('data param must be of pandas type DataFrame')
        elif len(data.columns) < 4:
            raise ValueError('Dataframe must contain at least 4 columns')
        elif index is not None and len(index) != 4:
            raise ValueError('index length must be 4')
        else:
            self.data = data
            sym_idx = 0
            date_idx = 1
            exp_idx = 2
            val_idx = 3

            if index is not None:
                # if index list is passed, infer the expiration column from the list
                sym_idx = index[0]
                date_idx = index[1]
                exp_idx = index[2]
                val_idx = index[3]

            expiries = self.data.iloc[:, exp_idx].unique()

            expiry_dates = [pd.to_datetime(str(t)).strftime('%Y-%m-%d') for t in expiries]

            self.option_chains = {date: pd.DataFrame for date in expiry_dates}

            # populate the dictionary
            for expiry_date in self.option_chains.keys():
                self.option_chains[expiry_date] = self.data[:][self.data["expiration"] == expiry_date]

            # normalize the option series
            self.results = {}
            for expiry_date in self.option_chains:
                # save some typing
                op = self.option_chains[expiry_date]
                col_names = op.columns.values

                # pivot the option_series
                pivotable = op.pivot(index=col_names[sym_idx], columns=col_names[date_idx], values=col_names[val_idx])

                if not pivotable.empty:
                    self.option_chains[expiry_date] = pivotable if not dropna else pivotable.dropna()

    def head(self, n=5):
        """
        Print the top n amount of expiry dates's option data
        :param n: The amount of expiry date's data to print starting from the first
        :return: None
        """
        for series in sorted(self.option_chains)[:n]:
            print(self.option_chains[series])

    def tail(self, n=5):
        """
        Print the bottom n amount of expiry dates's option data
        :param n: The amount of expiry date's data to print starting from the first
        :return: None
        """
        for series in sorted(self.option_chains)[-n:]:
            print(self.option_chains[series])

    def describe(self, periods=None, strikes=10):
        """

        :param periods:
        :param strikes:
        :return:
        """
        if periods is None:
            periods = [0, -1]

        for expiry in self.option_chains:
            temp = self.option_chains[expiry]
            # print(temp.iloc[:, 0])
            print(temp)
