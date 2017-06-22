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
                                                           str(row['symbol' + '_' +
                                                           str(row['offset'])]),
                                                           axis=1
                                                           )

        spread_chain = spread_chain[['spread_symbol', 'quote_date', 'expiration',
                                     'spread_bid', 'spread_ask', 'spread_mark',
                                     'spread_volume']]

        spread_chain = spread_chain.dropna()

        return spread_chain

    @staticmethod
    def single(leg):
        """
        A single call option position
        """
        pass
