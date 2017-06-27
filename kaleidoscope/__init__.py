# import data feed module

from kaleidoscope.options import option_filter
from . import datas, simulation, globals, strategies
from .datas import get

simulation.extend_pandas()
