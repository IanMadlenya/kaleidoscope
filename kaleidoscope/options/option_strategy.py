from kaleidoscope.globals import Period
from kaleidoscope.options.option_strategies import OptionStrategies


def vertical_spreads(quote_date, option_chains, strategy_params=None):
    """
    This filters for vertical spreads that expire within 7 weeks.

    :param quote_date: quote date of each call to the algo method
    :param option_chains: option chains for the quote date
    :param strategy_params
    :return: Dataframe containing all option chains that means the filtering criteria.
    """

    default_params = {
        'spread_width': 2,
        'expiration_period': Period.SEVEN_WEEKS
    }

    params = default_params if strategy_params is None else dict(default_params, **strategy_params)
    options = option_chains.lte('expiration', params['expiration_period']).fetch()

    # Batch create vertical call spreads on all strikes
    bear_call_spreads = OptionStrategies.vertical_spread(options, params['spread_width'])

    return bear_call_spreads
