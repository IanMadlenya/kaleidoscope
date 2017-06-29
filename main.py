import time

import kaleidoscope as kd


def start():

    # program timer
    program_starts = time.time()

    # define the options filter and strategy to analyse
    option_strategy = kd.option_filter.vertical_spreads_seven_weeks
    trading_strategy = kd.strategies.weekly_itm_vertical_credit_spreads

    # gather all historical option prices for VXX vertical call spreads for the specified expiration dates
    data = kd.get('VXX', start='2016-02-19', end='2016-02-19',
                  option_filter=option_strategy,
                  option_type='c'
                  )

    # SAMPLE USAGE =====================================================================
    # VXX_data = kd.get('VXX', start='2016-02-19', end='2016-02-19',
    #               option_filter=option_strategy,
    #               option_type='c'
    #               )
    #
    # UVXY_data = kd.get('UVXY', start='2016-02-19', end='2016-02-19',
    #               option_filter=option_strategy,
    #               option_type='c'
    #               )

    os = kd.OptionSeries(data, dropna=True)
    os.describe()

    program_ends = time.time()
    print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))

if __name__ == "__main__":
    start()
