import time
import kaleidoscope as kd


def start():

    # program timer
    program_starts = time.time()

    algo_params = {
        'spread_width': 2,
        'expiration_period': kd.globals.Period.SEVEN_WEEKS,
        'offset_pct': -0.10,
        'algo_name': 'vertical_spreads_seven_weeks'
    }

    # PROPOSED USAGE 1
    data = kd.get('VXX', start='2016-01-04', end='2016-01-08',
                  algo=kd.algos.algo_vertical_spreads_seven_weeks,
                  algo_params=algo_params,
                  option_type='c'
                  )

    # data.output_to_csv(algo_params['algo_name'])

    program_ends = time.time()
    print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))

if __name__ == "__main__":
    start()
