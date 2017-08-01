class BaseDataFeed(object):
    """
    Map columns from data source to the standard option columns used in the library.
    first position of tuple: column names used in program
    second position of tuple: column index of the source data that maps to the column in this program
                              -1 means do not map this column
    """

    def _normalize(self, dataframe, opt_params):
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

    def get(self, symbol, start, end,
            exclude_splits=False, option_type=None
            ):
        raise NotImplementedError("Subclass get method!")
