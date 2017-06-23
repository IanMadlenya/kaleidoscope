import time
import kaleidoscope as kd


def start():

    # program timer
    program_starts = time.time()

    # PROPOSED USAGE
    data = kd.get('VXX',
                  start='2016-01-04',
                  end='2016-02-19',
                  algo=kd.algos.vertical_call_spreads,
                  algo_params={
                      'spread_width': 2,
                      'expiration_period': kd.globals.Period.SEVEN_WEEKS
                  }
                  )

    print(data.head())

    program_ends = time.time()
    print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))

if __name__ == "__main__":
    start()
