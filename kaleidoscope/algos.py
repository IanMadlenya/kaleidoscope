from kaleidoscope.options.option_strategies import OptionStrategies
from kaleidoscope.options.option_query import OptionQuery
from kaleidoscope.globals import Period


def algo_vertical_spreads_seven_weeks(quote_date, option_chains, algo_params=None):
    """
    This filters for vertical spreads that expire within 7 weeks.

    :param quote_date: quote date of each call to the algo method
    :param option_chains: option chains for the quote date
    :param algo_params
    :return: Dataframe containing all option chains that means the filtering criteria.
    """

    options = option_chains.lte('expiration', Period.SEVEN_WEEKS).fetch()

    # Batch create vertical call spreads on all strikes
    bear_call_spreads = OptionStrategies.vertical_spread(options, algo_params['spread_width'])

    return bear_call_spreads


def algo_vertical_spreads_offset(quote_date, option_chains, algo_params=None):
    """
    Perform custom strategic logic to isolate option chains expiring
    within seven weeks and construct vertical spreads for the quote date.

    :param quote_date: quote date of each call to the algo method
    :param option_chains: option chains for the quote date
    :param algo_params
    :return: Dataframe containing prices for the specified option strategy
    """

    default_args = dict(spread_width=2, expiration_period=Period.ONE_WEEK)

    # TODO: apply dict merge algorithm here
    if algo_params is None:
        algo_params = default_args

    # TODO: add checks for all option types to be the same

    # Query and return a dataframe with call options expiring within the next 7 weeks
    underlying_price = option_chains.get_underlying_price()

    options = option_chains.lte('expiration', algo_params['expiration_period']).fetch()

    # Batch create vertical call spreads on all strikes
    bear_call_spreads = OptionStrategies.vertical_spread(options, algo_params['spread_width'])

    # Filter the spreads for ones created with short strikes at the specified offset pct.
    filtered_spreads = OptionQuery(bear_call_spreads)
    filtered_spreads = filtered_spreads.offset('lower_strike', underlying_price, algo_params['offset_pct']).fetch()

    return filtered_spreads
