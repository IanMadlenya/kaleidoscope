from datetime import date
from kaleidoscope.kaleidoscope import Kaleidoscope
from feeds.sqlite_reader import SQLiteReader

def start():

    start_date = date(2016, 1, 4)
    end_date = date(2016, 1, 31)

    # Retrieve options data stored in a sqlite database for development.
    # It is recommended to store options data in a database.
    sql_data = SQLiteReader(start_date, end_date, upper_delta=0.95, lower_delta=0.05)
    sql_data.subscribe_options("VXX")

    kd = Kaleidoscope()
    kd.set_datafeed(sql_data)

if __name__ == "__main__":
    start()
