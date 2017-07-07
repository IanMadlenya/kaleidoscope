import time

import kaleidoscope as kd
from kaleidoscope.globals import OptionType


def start():

    # program timer
    program_starts = time.time()

    # VXX Call Credit Spreads vs. Put Debit Spreads ==========================================

    data = kd.get('VXX', start='2016-02-19', end='2016-02-19')
    strategy = kd.option_strategy.vertical_spreads

    # construct put vertical spreads (returns OptionSeries object)
    put_spreads = kd.construct(kd.option_strategy.vertical_spreads, data, option_type=OptionType.PUT)

    # construct call vertical spreads (returns OptionSeries object)
    # call_spreads = kd.construct(strategy, data, option_type=OptionType.CALL)

    # construct custom spreads
    # custom_spread = kd.construct(kd.option_strategy.custom, data)

    # construct iron condor with convenience method
    # iron_condor = kd.construct(kd.option_strategy.iron_condors, data)

    # plot period vs prices for all expiry cycles, should automatically rebase each expiration data set
    # perf.plot()

    # add a different scenario to do side by side comparison
    # perf.add_scenario(spread_value=1.50)
    # perf.plot()

    # what about selling spreads for credits 0.50, 1.00, 1.50
    # perf_multi = data.calc_stats(spread_value=(0.5, 1.0, 1.5))
    # perf_multi.describe()
    # perf_multi.plot()

    # describe the statistics if we were to sell in the last 3 weeks?
    # perf_multi.set_range(period_start=kd.globals.Period.LAST_3_WEEKS)
    # perf_multi.describe()

    # what are the expected values of each credit amount?
    # perf_multi.calc_expected_values()
    # perf_multi.calc_actual_expected_values()

    program_ends = time.time()
    print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))

if __name__ == "__main__":
    start()
