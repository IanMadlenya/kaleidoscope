from kaleidoscope.globals import Period, OptionType
from kaleidoscope.options.option_strategies import OptionStrategies


def vertical_spreads(quote_date, option_chains, **kwargs):
    """
    This filters for option with DTE within 7 weeks and constructs vertical spreads
    with the filtered option chain for the quote date

    :param quote_date: quote date of each call to the algo method
    :param option_chains: option chains for the quote date
    :param kwargs: various options for creating option spreads, passed into option strategy function
    :return: Dataframe containing all option chains that means the filtering criteria.
    """

    params = {
        'width': 2,
        'DTE': Period.SEVEN_WEEKS,
        'option_type': OptionType.CALL
    }

    params.update(kwargs)

    # pre-filter the options to create the option spread with
    chains = (option_chains.lte('expiration', params['DTE'])
              .option_type(params['option_type'])
              .fetch()
              )

    # Batch create vertical call spreads on all strikes
    vertical_spreads = OptionStrategies.vertical_spread(chains, width=params['width'])

    return vertical_spreads


def iron_condors(quote_date, option_chains, **kwargs):
    """
    This filters for option with DTE within 7 weeks and constructs iron condors
    with the filtered option chain for the quote date

    :param quote_date: quote date of each call to the algo method
    :param option_chains: option chains for the quote date
    :param kwargs: various options for creating option spreads, passed into option strategy function
    :return: Dataframe containing all option chains that means the filtering criteria.
    """

    params = {
        'DTE': Period.SEVEN_WEEKS,
        'call_spread_width': 2,
        'put_spread_width': 2
    }

    params.update(kwargs)

    # pre-filter the options to create the option spread with
    chains = (option_chains.lte('expiration', params['DTE']).fetch())

    # Batch create vertical call spreads on all strikes
    iron_condors = OptionStrategies.iron_condor(chains,
                                                call_spread_width=params['call_spread_width'],
                                                put_spread_width=params['put_spread_width']
                                                )

    return iron_condors


def custom(quote_date, option_chains, **kwargs):
    pass
