# import data feed module

from pandas.core.base import PandasObject

from kaleidoscope.options import option_strategy
from . import datas, globals, strategies, performance
from .datas import get
from .option_series import OptionSeries
from .options.option_strategies import construct

PandasObject.output_to_csv = datas.output_to_csv
