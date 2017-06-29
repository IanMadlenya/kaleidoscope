class OptionStrategies(object):
    """
    Static methods to define option strategies
    """
    @staticmethod
    def generate_offsets(dataframe, shift_col, offsets):
        """
        :param dataframe: Dataframe to attach new offset columns to
        :param shift_col: The column to create new shifted columns for
        :param offsets: Array of offset values to generate offsetting columns for
        :return: None
        """
        offsets = offsets.sort_values(ascending=False)

        for offset in offsets:
            col = shift_col + "_" + str(offset)
            dataframe[col] = dataframe[shift_col].shift(offset)

    @staticmethod
    def moneyness(option_type, underlying, h_strike, l_strike):
        """
        Determine the moneyness of an option
        :param option_type: option type, 'c' or 'p'
        :param underlying: price of the underlying asset of option
        :param h_strike: higher strike of the spread
        :param l_strike: lower strike of the spread
        :return: distance between the higher strike and underlying if puts,
                 distance between the lower strike and underlying if calls
        """
        # TODO: may want to normalize option_type coming in from data source
        if (option_type == 'c' and underlying < l_strike) or (option_type == 'p' and underlying > h_strike):
            return "ITM"
        elif (option_type == 'c' and underlying > l_strike) or (option_type == 'p' and underlying < h_strike):
            return "OTM"
        elif (option_type == 'c' and underlying == l_strike) or (option_type == 'p' and underlying == h_strike):
            return "ATM"

    @staticmethod
    def vertical_spread(chain, width):
        """

        :param chain: Dataframe to manipulate and base vertical spreads on.
        :param width: Distance in value between the strikes to construct vertical spreads with.
        :return: A new dataframe containing all vertical spreads created from dataframe

        The vertical spread is an option spread strategy whereby the
        option trader purchases a certain number of options and simultaneously
        sell an equal number of options of the same class, same underlying security,
        same expiration date, but at a different strike price.
        """
        spread_chain = chain.copy()

        # TODO: Thoroughly test this algorithm for widths with .25, .5, 10, 50, etc increments
        # Calculate the distance of the strikes between each row
        spread_chain['dist'] = spread_chain['strike'].shift(width * -1) - spread_chain['strike']

        # Calculate the factor between the distance and the specified width
        spread_chain['factor'] = spread_chain['dist'] / width

        # Using the specified width and factor, calculate the offset for each row
        spread_chain['offset'] = -1 * width / spread_chain['factor']
        spread_chain['offset'] = spread_chain['offset'].round(0)

        # Clean up the data
        spread_chain = spread_chain.dropna()
        spread_chain['offset'] = spread_chain['offset'].astype(int)
        spread_chain = spread_chain.drop(['dist', 'factor'], axis=1)

        # generate the offsetting columns for each offset value
        offsets = spread_chain['offset'].value_counts().index
        OptionStrategies.generate_offsets(spread_chain, 'strike', offsets)
        OptionStrategies.generate_offsets(spread_chain, 'ask', offsets)
        OptionStrategies.generate_offsets(spread_chain, 'bid', offsets)
        OptionStrategies.generate_offsets(spread_chain, 'trade_volume', offsets)
        OptionStrategies.generate_offsets(spread_chain, 'symbol', offsets)

        # calculate the spread's bid and ask prices
        spread_chain['spread_bid'] = spread_chain.apply(lambda row: row['bid'] -
                                                        row['ask' + '_' +
                                                        str(row['offset'])],
                                                        axis=1
                                                        )

        spread_chain['spread_ask'] = spread_chain.apply(lambda row: row['ask'] -
                                                        row['bid' + '_' +
                                                        str(row['offset'])],
                                                        axis=1
                                                        )

        spread_chain['spread_mark'] = spread_chain.apply(lambda row: (row['spread_bid'] +
                                                         row['spread_ask']) / 2,
                                                         axis=1
                                                         )

        # sum the trade volume of the two strikes
        spread_chain['spread_volume'] = spread_chain.apply(lambda row: row['trade_volume'] +
                                                           row['trade_volume' + '_' +
                                                           str(row['offset'])],
                                                           axis=1
                                                           )

        # sum the trade volume of the two strikes
        spread_chain['spread_symbol'] = spread_chain.apply(lambda row: "." + row['symbol'] + "-." +
                                                                       str(row['symbol' + '_' + str(row['offset'])]),
                                                           axis=1
                                                           )

        spread_chain.rename(columns={'strike': 'lower_strike'}, inplace=True)

        # get the higher strike of the spread
        spread_chain['higher_strike'] = spread_chain.apply(lambda row: row['strike' + '_' +
                                                                           str(row['offset'])],
                                                           axis=1
                                                           )

        # clean up the results, drop NaN
        spread_chain = spread_chain.dropna()

        # check distance equals specified width, trim distances that do not match the width
        spread_chain['dist_check'] = spread_chain['higher_strike'] - spread_chain['lower_strike']
        spread_chain = spread_chain[spread_chain['dist_check'] == float(width)]

        spread_chain = spread_chain[['spread_symbol', 'quote_date', 'expiration', 'spread_mark',
                                     'underlying_price', 'lower_strike', 'higher_strike']]

        return spread_chain
