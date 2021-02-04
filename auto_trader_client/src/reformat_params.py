"""Functions to reformat parsed text dictionary after it has been validated"""


def reformat_params(order_params):
    """Reformat order parameters before generating order. Takes dictionary of parsed text
    and returns reformatted dictionary"""

    # remove superfluous zeroes from strike price
    strike = float(order_params["strike_price"])
    if strike % 1 == 0:
        order_params["strike_price"] = str(int(strike))
    elif strike % 0.5 == 0:
        order_params["strike_price"] = str(strike)
    else:
        raise ValueError(f"Strike price is {strike}; an illegal value")

    # convert expiration string to datetime object for tda package
    order_params["expiration"] = expiration_str_to_datetime(order_params["expiration"])
    return order_params


def expiration_str_to_datetime(exp_str):
    """Returns datetime object from expiration date string.
    Expected input is string formatted as month/day or month/day/year(2 or 4 digits)"""
    import datetime

    split_exp = exp_str.split("/")
    if len(split_exp) == 2:
        month_str, day_str = split_exp
        # assume expiration without year has expiration of current year
        year = datetime.datetime.today().year
        return datetime.datetime(year, int(month_str), int(day_str))
    elif len(split_exp) == 3:
        month_str, day_str, yr_str = split_exp
        if len(yr_str) == 2:
            yr_str = "20" + yr_str
        return datetime.datetime(int(yr_str), int(month_str), int(day_str))
