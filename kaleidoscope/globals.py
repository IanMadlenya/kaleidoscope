import sys
from enum import Enum

if sys.version_info > (3, 0):
    # Python 3 code in this block
    import pathlib

    PROJECT_DIR = str(pathlib.Path(__file__).parents[1])
else:
    # Python 2 code in this block
    import pathlib2

    PROJECT_DIR = str(pathlib2.Path(__file__).parents[1])

DATA_SUB_DIR = "data"
OUTPUT_DIR = "output"
TEST_DIR = "tests"
FIXTURES = 'fixtures'
DB_NAME = "securities"


class Period(Enum):
    DAY = 1
    TWO_DAYS = 2
    THREE_DAYS = 3
    FOUR_DAYS = 4
    FIVE_DAYS = 5
    SIX_DAYS = 6
    ONE_WEEK = 7
    TWO_WEEKS = 14
    THREE_WEEKS = 21
    FOUR_WEEKS = 28
    FIVE_WEEKS = 35
    SIX_WEEKS = 42
    SEVEN_WEEKS = 49


class OrderAction(Enum):
    BUY = 1
    SELL = -1

class OptionType(Enum):
    CALL = ('c', 1)
    PUT = ('p', -1)


class Moneyness(Enum):
    ITM = "ITM"
    OTM = "OTM"
    ATM = "ATM"

OrderType = Enum("OrderType", "MKT, LMT")
OrderStatus = Enum("OrderStatus", "WORKING, REJECTED, FILLED, DELETED, EXPIRED")
OrderTIF = Enum("OrderTIF", "GTC, DAY")

EventType = Enum("EventType", "DATA, ORDER, FILL, REJECTED, EXPIRED")
SecType = Enum("SecType", "STK, OPT")
