def weekly_itm_vertical_credit_spreads(pivotable, credit_target=1.00, start_idx=0, end_idx=-1):
    """
    Search for vertical spreads priced at or closest to one dollar for each expiration cycle.

    :param pivotable: A dictionary where 'key' is each expiration date of the simulation time frame,
                          'value' is a DataFrame of all options that traded to that expiration date
    :param credit_target: The amount of credit to aim to sell for in this strategy
    :param start_idx:
    :param end_idx:
    :return: A dataframe representing a set of option trades that this strategy executed.
    """

    # TODO: check the name of option_series contains 'vertical spreads'
    # Make sure the correct option filter was applied prior to running this strategy

    pivotable = pivotable.iloc[:, [start_idx, end_idx]].dropna()

    # query = OptionQuery(pivotable, inplace=True)

    # Here we select the spread that is priced closest to one dollar.
    # If this selection returns more than one spread that is priced closest to one dollar
    # we choose the higher priced spread.
    # return query.closest('spread_mark', credit_target).max('spread_mark')

    return pivotable
