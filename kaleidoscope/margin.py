from kaleidoscope.globals import OrderAction


def tos_margin(strategy, action):
    if strategy.name == "single":
        return strategy.mark
    elif strategy.name == "calendar":
        pass
    elif strategy.name == "combo":
        pass
    else:
        if action == OrderAction.BUY:
            # debit spread, margin is % of debit
            return strategy.mark
        else:
            # credit spread
            return strategy.max_strike_width - strategy.mark
