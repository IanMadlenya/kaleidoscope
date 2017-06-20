import time
from datetime import date
from feeds.sqlite_reader import SQLiteReader
from kaleidoscope.kaleidoscope import Kaleidoscope
from kaleidoscope.patterns.sample_pattern import SamplePattern

def start():

    # program timer
    program_starts = time.time()

    # set time period to look up historical data
    start_date = date(2016, 1, 4)
    end_date = date(2016, 2, 19)

    # restrict on options with expiration less than this date
    expiration = date(2017, 2, 28)

    # Retrieve options data stored in a sqlite database for development.
    # It is recommended to store options data in a database.
    sql_data = SQLiteReader(start_date, end_date, expiration,
                            upper_delta=1, lower_delta=0
                           )

    sql_data.subscribe_options("VXX")

    session = Kaleidoscope(option_feed=sql_data)
    session.add_pattern(SamplePattern, SPREAD_WIDTH=2, WEEKDAY_START=4)
    session.run()

    program_ends = time.time()
    print("The simulation ran for {0} seconds."
          .format(round(program_ends - program_starts, 2))
         )

if __name__ == "__main__":
    start()
