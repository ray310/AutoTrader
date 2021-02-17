"""Functions used validate and reformat order parameters (parsed text) dictionary"""


def validate_params(order_params):
    """Validates parsed text signal before order is generated.
    Takes order parameters dictionary. Returns True is valid, else False"""
    import logging

    try:
        assert isinstance(order_params["instruction"], str)
        assert (
            order_params["instruction"] == "BTO" or order_params["instruction"] == "STC"
        )
        assert isinstance(order_params["ticker"], str) is True
        assert 0 < len(order_params["ticker"]) < 6
        assert order_params["ticker"] == order_params["ticker"].upper()
        assert isinstance(order_params["strike_price"], str) is True
        assert float(order_params["strike_price"]) >= 1
        assert float(order_params["strike_price"]) < 100000  # less than $100,000
        assert float(order_params["strike_price"]) % 0.5 == 0
        assert isinstance(order_params["contract_type"], str)
        assert (
            order_params["contract_type"] == "C" or order_params["contract_type"] == "P"
        )
        assert isinstance(order_params["contract_price"], str) is True
        assert 0 < float(order_params["contract_price"]) < 1000
        if not is_expiration_valid(order_params["expiration"]):
            raise ValueError
    except (AssertionError, ValueError, KeyError):
        str_params = str(order_params)
        logging.warning(f"{str_params} failed validation")
        return False
    else:
        return True


def is_expiration_valid(date_str):
    """Returns True if date string is valid, else False.
    Valid date string should be valid date from within 4 years formatted as
    month/day or month/day/year (2 or 4 digit year)"""
    import datetime
    import logging

    try:
        assert isinstance(date_str, str)
        assert 1 <= date_str.count("/") <= 2
        current_yr = datetime.datetime.today().year
        expiration_lst = date_str.split("/")
        if len(expiration_lst) == 2:
            month_str, day_str = expiration_lst
            datestamp = datetime.datetime(current_yr, int(month_str), int(day_str))
        elif len(expiration_lst) == 3:
            month_str, day_str, yr_str = expiration_lst
            if len(yr_str) == 2:
                yr_str = "20" + yr_str
            datestamp = datetime.datetime(int(yr_str), int(month_str), int(day_str))
        else:
            return False
        assert datestamp.year <= current_yr + 3  # not more than 3 years in future
        assert not expired(datestamp)  # ensure expiration has not passed
    except (AssertionError, ValueError):
        date_str = str(date_str)
        logging.warning(f"{date_str} failed validation")
        return False
    else:
        return True


def expired(dt_obj):
    """Return True if datetime.datetime obj is not before current date.
    Return False if date occurs in past"""
    import datetime

    dt = datetime.date.today()
    dt = datetime.datetime(dt.year, dt.month, dt.day)
    return dt_obj < dt


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

    order_params["contract_price"] = float(order_params["contract_price"])

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
