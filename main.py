import time

import kaleidoscope as kd


def start():

    # program timer
    program_starts = time.time()

    # gather all historical option prices for VXX vertical call spreads for the specified expiration dates
    data = kd.get('VXX', start='2016-02-19', end='2016-12-31',
                  option_strategy=kd.option_strategy.vertical_spreads,
                  option_type='c'
                  )

    # show results for selling vertical call spreads for 1.00 credit
    perf = data.calc_stats(spread_values=(1.0,))
    perf.describe()

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
