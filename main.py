import time

import kaleidoscope as kd


def start():

    # program timer
    program_starts = time.time()

    # VXX Call Credit Spreads vs. Put Debit Spreads ==========================================
    data = kd.get('VXX', start='2016-02-19', end='2016-02-19')

    # construct call vertical spreads (returns OptionSeries object)
    # call_spreads = kd.construct(kd.OptionStrategies.vertical_spread,
    #                             data,
    #                             option_type=kd.OptionType.CALL,
    #                             DTE=kd.Period.THREE_WEEKS,
    #                             width=2
    #                             )

    # iron_condors = kd.construct(kd.OptionStrategies.iron_condor,
    #                             data,
    #                             DTE=kd.Period.SEVEN_WEEKS,
    #                             width=10,
    #                             c_width=2,
    #                             p_width=2
    #                             )

    covered_stock = kd.construct(kd.OptionStrategies.covered_stock,
                                 data,
                                 option_type=kd.OptionType.PUT
                                 )

    program_ends = time.time()
    print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))

    covered_stock.plot('2016-02-19')

if __name__ == "__main__":
    start()
