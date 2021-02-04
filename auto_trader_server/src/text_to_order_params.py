""" Takes text data and parses it for specified pattern to generate order parameters """


def text_to_order_params(string):
    """ Parses string for signal. If string contains one and only one order signal,
    then it returns the order parameters as strings and any additional comments,
    else returns None
    Format example:
        'STC INTC 50C 12/31 @.45'
        <Open/close> <ticker> <strike price + call or put> <expiration date> <@ price>
    """
    import logging
    import re

    # Regex Formatting
    # () denote regex groupings. Regex 'or' uses short-circuit evaluation
    # (?<!\S) is negative lookbehind assertion for any non-whitespace character
    # BTO/STC cannot be preceded by any word character
    instruction = "((?<!\S)BTO|(?<!\S)STC)"
    ticker_pattern = "([A-Z]{1,5})"  # 1-5 capitalized letters

    # 1-5 numbers with optional two decimals
    strike_price = "([0-9]{1,5}\.[0-9]{1,2}|[0-9]{1,5})"
    contract_type = "([CP]{1})"  # either C or P

    # can be month/day/year(2 or 4 digit year) or month/day
    # month and day can be 1-2 digits
    expiration_date = "([0-9]{1,2}/[0-9]{1,2}/[0-9]{4}|[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}|[0-9]{1,2}/[0-9]{1,2})"

    # (?!\S) is negative lookahead assertion for any non-whitespace character
    # up to 3 digit number followed by 1-2 decimals
    contract_price = "([0-9]{0,3}\.[0-9]{1,2}(?!\S))"
    space = "\s{1,2}"  # 1-2 spaces
    at = "@\s{0,1}"  # @ followed by 0-1 spaces
    regex_pattern = (
        instruction
        + space
        + ticker_pattern
        + space
        + strike_price
        + contract_type
        + space
        + expiration_date
        + space
        + at
        + contract_price
    )

    # Outputs
    order_params = {
        "instruction": None,
        "ticker": None,
        "strike_price": None,
        "contract_type": None,
        "expiration": None,
        "contract_price": None,
        "comments": None,
    }

    # Text should contain one and only one order signal
    matches = [match for match in re.finditer(regex_pattern, string)]
    if len(matches) == 0:
        logging.info("String did not match signal pattern")
    elif len(matches) == 1:
        match = matches[0]  # match is re.Match object
        match.groups()
        order_params["instruction"] = match.group(1)
        order_params["ticker"] = match.group(2)
        order_params["strike_price"] = match.group(3)
        order_params["contract_type"] = match.group(4)
        order_params["expiration"] = match.group(5)
        order_params["contract_price"] = match.group(6)
        start, end = match.span()
        comments = string[0:start] + string[end:]
        if comments != "":
            order_params["comments"] = comments
    else:
        logging.warning("Two or matches detected in string")

    if order_params == {
        "instruction": None,
        "ticker": None,
        "strike_price": None,
        "contract_type": None,
        "expiration": None,
        "contract_price": None,
        "comments": None,
    }:
        return None
    else:
        return order_params
