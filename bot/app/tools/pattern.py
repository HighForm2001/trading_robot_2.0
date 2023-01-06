def pivot_point(previous, current, next,mode,previous_2 = None, next_2 = None ):
    """If mode == 1, find swing low, elif mode == 2, find swing high"""
    if mode == 1:
        if previous_2 and next_2:
            if previous > current and next > current and previous_2 > current and next_2 > current:
                return True
            return False
        if previous > current and next > current:
            return True
        return False
    else:
        if previous_2 and next_2:
            if previous < current and next < current and previous_2 < current and next_2 < current:
                return True
            return False
        if previous < current and next < current:
            return True

        return False


def imbalance(previous, current, next, direction):
    body_low = min(current.open, current.close)
    body_high = max(current.open, current.close)
    if direction == "Bearish":
        if body_low < previous.low:  # look for bearsh imbalance
            if next.high < previous.low:  # imbalance found.
                area_high = min(body_high, previous.low)
                area_low = max(body_low, next.high)
                return True, [area_low, area_high]
    if direction == "Bullish":
        if body_high > previous.high:  # look for bullish imbalance
            if next.low > previous.high:  # imbalance found.
                area_high = min(body_high, next.low)
                area_low = max(body_low, previous.high)
                return True, [area_low, area_high]
    return False, None


def check_candle_type(open, close):
    if open < close:  # Bullish
        return 1
    return 0  # Bearish
