import kaleidoscope as kd

# initialize the backtest
bt = kd.Backtest()
bt.add_opt_strategy(kd.strategies.SimpleBuySell,
                    symbol=("VXX",),
                    width=range(1, 6),
                    price=(0.5, 0.75, 1)
                    )
bt.run()
