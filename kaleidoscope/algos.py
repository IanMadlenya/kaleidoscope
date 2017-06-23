from kaleidoscope.options.option_strategies import OptionStrategies
from kaleidoscope.globals import Period


def vertical_call_spreads(quote_date, option_chains, algo_params=None):
    """
    Perform custom strategic logic to isolate option chains expiring
    within seven weeks and construct vertical spreads for the quote date.

    :param quote_date: quote date of each call to the algo method
    :param option_chains: option chains for the quote date
    :param algo_params
    :return: Dataframe containing prices for the specified option strategy
    """

    default_args = {
        'spread_width': 2,
        'expiration_period': Period.ONE_WEEK
    }

    if algo_params is None:
        algo_params = default_args

    # Query and return a dataframe with call options expiring within the next 7 weeks
    options = option_chains['VXX'].lte('expiration', algo_params['expiration_period']).calls().fetch()

    # Batch create vertical call spreads on all strikes
    bear_call_spreads = OptionStrategies.vertical_spread(options, algo_params['spread_width'])

    return bear_call_spreads
