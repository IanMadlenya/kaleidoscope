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

bt = kd.Backtest()
bt.get_data('VXX', start='2016-02-19', end='2016-02-19')
bt.add_strategy(kd.strategies.SimpleBuySell,
                option_type=kd.OptionType.CALL,
                DTE=kd.Period.SEVEN_WEEKS,
                width=2
                )
bt.run()
