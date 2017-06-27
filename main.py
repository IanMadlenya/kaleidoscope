import time

import kaleidoscope as kd


def start():

    # program timer
    program_starts = time.time()

    # gather all historical option prices for VXX for the specified expiration dates
    data = kd.get('VXX', start='2016-02-19', end='2016-02-26',
                  option_filter=kd.option_filter.vertical_spreads_seven_weeks,
                  option_type='c'
                  )

    data.simulate(strategy=kd.strategies.weekly_itm_vertical_credit_spreads)

    program_ends = time.time()
    print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))

if __name__ == "__main__":
    start()
