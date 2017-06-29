import pathlib
from enum import Enum

PROJECT_DIR = pathlib.Path(__file__).parents[1]
DATA_SUB_DIR = "data"
OUTPUT_DIR = "output"
FILE_NAME = "securities"

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


class Action(Enum):
    BUY = 1
    SELL = -1
