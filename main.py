import kaleidoscope as kd

# Analysis Use Case ===================================================

# data = kd.get('VXX', start=start_date, end=end_date)
#
# # construct call vertical spreads (returns OptionSeries object)
# call_spreads = kd.construct(kd.OptionStrategies.vertical,
#                             data,
#                             option_type=kd.OptionType.CALL,
#                             DTE=kd.Period.THREE_WEEKS,
#                             width=2
#                             )

# Backtesting Use Case =================================================

# grab the backtest data
data = kd.get('VXX', start='2016-02-19', end='2016-02-19')

# initialize the backtest
bt = kd.Backtest()

# add the datafeed to backtest
bt.add_data(data)

bt.add_strategy(kd.strategies.SimpleBuySell,
                option_type=kd.OptionType.CALL,
                DTE=kd.Period.SEVEN_WEEKS,
                width=2
                )
bt.run()
