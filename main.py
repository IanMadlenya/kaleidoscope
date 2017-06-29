import time

import kaleidoscope as kd


def start():

    # program timer
    program_starts = time.time()

    # define the options filter and strategy to analyse
    option_strategy = kd.option_filter.vertical_spreads_seven_weeks

    # gather all historical option prices for VXX vertical call spreads for the specified expiration dates
    data = kd.get('VXX', start='2016-02-19', end='2016-02-26',
                  option_filter=option_strategy,
                  option_type='c'
                  )

    # show results for selling vertical call spreads at 1.00 credit
    data.describe(prices=1.00)

    program_ends = time.time()
    print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))

if __name__ == "__main__":
    start()
