import time
from datetime import date
from feeds.sqlite_reader import SQLiteReader
from kaleidoscope.kaleidoscope import Kaleidoscope
from kaleidoscope.patterns.sample_pattern import SamplePattern


def start():

    # program timer
    program_starts = time.time()

    # initialize an instance of Kaleidoscope and run analysis
    session = Kaleidoscope(option_feed=SQLiteReader())
    session.add_pattern(SamplePattern, SPREAD_WIDTH=2, WEEKDAY_START=4)
    session.run()

    program_ends = time.time()
    print("The simulation ran for {0} seconds.".format(round(program_ends - program_starts, 2)))

if __name__ == "__main__":
    start()
