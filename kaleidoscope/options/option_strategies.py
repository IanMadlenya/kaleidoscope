from kaleidoscope.globals import OrderAction

class OptionStrategies(object):
    """
    Static methods to define option strategies
    """
    @staticmethod
    def vertical_spread(chain, width, side=OrderAction.SELL):
        """
        The vertical spread is an option spread strategy whereby the
        option trader purchases a certain number of options and simultaneously
        sell an equal number of options of the same class, same underlying security,
        same expiration date, but at a different strike price.
        """
        spread_chain = chain.copy()

         # for each strike, shift the ask price by the spread width
        strikes = chain['strike'].values
        shift_dist = side.value * int(width/(strikes[1] - strikes[0]))

        spread_chain.ask = spread_chain.ask.shift(shift_dist)
        spread_chain['trade_price'] = abs(spread_chain.bid - spread_chain.ask)

        # rename 'strike' column to 'short strike'
        spread_chain = spread_chain.rename(columns={'strike': 'short_strike'})

        # add short or long strike prices to dataframe
        spread_chain.insert(4, 'long_strike', spread_chain['short_strike'] - shift_dist)

        if side == OrderAction.SELL:
            # calculate spread's open and close price
            spread_chain['open'] = spread_chain['open'] - spread_chain['open'].shift(shift_dist)
            spread_chain['close'] = spread_chain['close'] - spread_chain['close'].shift(shift_dist)
        elif side == OrderAction.BUY:
            abs_shift_dist = abs(shift_dist)
            spread_chain['open'] = spread_chain['open'].shift(abs_shift_dist) - spread_chain['open']
            spread_chain['close'] = spread_chain['close'].shift(abs_shift_dist) - \
                                    spread_chain['close']

        # sum trade volume of both legs to get total volume for spread
        spread_chain['trade_volume'] = spread_chain['trade_volume'].shift(shift_dist) + \
                                       spread_chain['trade_volume']

        # generate spread symbol
        spread_chain['spread_symbol'] = "." + spread_chain['symbol'] + \
                                        "-." + spread_chain['symbol'].shift(shift_dist)

        spread_chain = spread_chain.dropna()
        spread_chain.set_index('spread_symbol', inplace=True)
        spread_chain = spread_chain.drop(['symbol', 'bid', 'ask', 'high', \
                                          'low', 'underlying_price', 'option_type'], axis=1)

        return spread_chain

    @staticmethod
    def single(leg):
        """
        A single call option position
        """
        pass
