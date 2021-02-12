"""Functions needed to execute TD Ameritrade orders"""

import sys
import tda
import tda.orders.options
import json
import logging
from src.client_settings import (
    TD_TOKEN_PATH,
    TD_AUTH_PARAMS_PATH,
    TD_DICT_KEY_API,
    TD_DICT_KEY_URI,
    TD_DICT_KEY_ACCT,
    ORD_SETTINGS_PATH,
    ORD_VAL_KEY,
    BUY_LIM_KEY,
    SL_KEY,
)


def initialize_order(ord_params):
    """Initialize TDA and order related values,
    authenticate with TDA site and place order"""

    # initialize values
    td_acct = {}
    with open(TD_AUTH_PARAMS_PATH) as fp:
        td_auth_params = json.load(fp)
    td_acct["uri"] = td_auth_params[TD_DICT_KEY_URI]
    td_acct["api_key"] = td_auth_params[TD_DICT_KEY_API]
    td_acct["acct_num"] = td_auth_params[TD_DICT_KEY_ACCT]

    with open(ORD_SETTINGS_PATH) as fp:
        order_settings = json.load(fp)
    usr_set = {
        "max_ord_val": order_settings[ORD_VAL_KEY],  # max $ value of order e.g. 500.00
        "buy_limit_percent": order_settings[BUY_LIM_KEY],
        "SL_percent": order_settings[SL_KEY],
    }

    # check user inputs
    validate_user_settings(usr_set)

    # authenticate
    client = authenticate_tda_account(TD_TOKEN_PATH, td_acct["api_key"], td_acct["uri"])

    # generate and place order
    if ord_params["instruction"] == "BTO":
        buy_qty = calc_buy_order_quantity(
            ord_params["contract_price"],
            usr_set["max_ord_val"],
            usr_set["buy_limit_percent"],
        )
        if buy_qty >= 1:
            ota_order = build_bto_order_w_stop_loss(
                ord_params,
                buy_qty,
                usr_set["buy_limit_percent"],
                usr_set["SL_percent"],
            )
            response = client.place_order(td_acct["acct_num"], order_spec=ota_order)
            logging.info(response)
        else:
            msg1 = f"{ord_params} purchase quantity is 0\n"
            msg2 = (
                "This may be due to a low max order value or high buy limit percent\n\n"
            )
            sys.stderr.write(msg1 + msg2)
    elif ord_params["instruction"] == "STC":
        symbol = build_option_symbol(ord_params)
        position_qty = get_position_quant(client, td_acct["acct_num"], symbol)
        if position_qty >= 1:
            existing_stc_ids = get_existing_stc_orders(
                client, td_acct["acct_num"], symbol
            )
            if len(existing_stc_ids) > 0:
                for ord_id in existing_stc_ids:
                    response = client.cancel_order(ord_id, td_acct["acct_num"])
                    logging.info(response)
            # TODO: Future feature: If sell_half flag then
            #  stc_market half and stc_stop_market other half
            stc = build_stc_market_order(ord_params, position_qty)
            response = client.place_order(td_acct["acct_num"], order_spec=stc)
            logging.info(response)
    else:
        instr = ord_params["instruction"]
        logging.warning(f"Invalid order instruction: {instr}")


# creating more than one client will likely cause issues with authentication
def authenticate_tda_account(token_path: str, api_key: str, redirect_uri: str):
    """Takes TDA app key and path to locally stored auth token and tries to authenticate.
    If unable to authenticate with token, performs backup authentication
    from login auth flow. Returns authenticated client_tests object"""
    client = None
    try:
        # tda.auth automatically creates and updates token file at token_path
        client = tda.auth.client_from_token_file(token_path, api_key)
    except FileNotFoundError:
        # should on first log-in before token has been retrieved and saved by tda.auth
        from src.client_settings import GECKODRIVER_PATH
        from selenium import webdriver

        # Note that the webdriver executable for your OS must be downloaded and
        # saved at the set path. Other webdrivers like Chrome can also be used
        with webdriver.Firefox(executable_path=GECKODRIVER_PATH) as driver:
            client = tda.auth.client_from_login_flow(
                driver, api_key, redirect_uri, token_path
            )

    return client


def build_bto_order_w_stop_loss(
    ord_params: dict, qty: int, limit_percent: float, stop_loss_percent: float
):
    """Prepares and returns OrderBuilder object for one-trigger another order.
    First order is BTO limit and second order is STC stop-market"""

    # prepare BTO inputs
    buy_lim_price = round(ord_params["contract_price"] * (1 + limit_percent), 2)
    stop_loss_price = round(ord_params["contract_price"] * (1 - stop_loss_percent), 2)
    option_symbol = build_option_symbol(ord_params)

    # prepare pre-filled OrderBuilder objs
    bto_lim = tda.orders.options.option_buy_to_open_limit(
        option_symbol, qty, buy_lim_price
    )
    stc_stop_market = build_stc_stop_market(option_symbol, qty, stop_loss_price)
    one_trigger_other = tda.orders.common.first_triggers_second(
        bto_lim, stc_stop_market
    )
    return one_trigger_other


def build_stc_market_order(ord_params: dict, pos_qty: float):
    """ Returns STC market order OrderBuilder obj"""
    option_symbol = build_option_symbol(ord_params)
    stc = tda.orders.options.option_sell_to_close_market(option_symbol, pos_qty)
    return stc


def calc_buy_order_quantity(price: float, max_ord_val: float, limit_percent: float):
    """Returns the order quantity (int) for a buy order based on
    the option price, maximum order size, and buy limit percent  """
    lot_size = 100  # standard lot size value
    lot_value = price * lot_size * (1 + limit_percent)
    quantity = max_ord_val / lot_value
    return int(quantity)  # int() rounds down


def build_option_symbol(ord_params: dict):
    """ Returns option symbol as string from order parameters dictionary.
    Note that expiration_date must be datetime.datetime object"""
    symbol_builder_class = tda.orders.options.OptionSymbol(
        underlying_symbol=ord_params["ticker"],
        expiration_date=ord_params["expiration"],  # datetime.datetime obj
        contract_type=ord_params["contract_type"],
        strike_price_as_string=ord_params["strike_price"],
    )
    # OptionSymbol class does not return symbol until build method is called
    symbol = symbol_builder_class.build()
    return symbol


def build_stc_stop_market(symbol: str, qty: int, stop_price: float):
    """Return an OrderBuilder object for a STC stop-market order"""
    ord = tda.orders.options.option_sell_to_close_market(symbol, qty)
    ord.set_order_type(tda.orders.common.OrderType.STOP)
    trunc_price = round(stop_price, 2)
    ord.set_stop_price(trunc_price)  # truncated float
    ord.set_duration(tda.orders.common.Duration.GOOD_TILL_CANCEL)
    return ord


# get shares in existing position
def get_position_quant(client, acct_id: str, symbol: str):
    """Takes client, account_id, and symbol to search for.
    Returns position long quantity for symbol"""
    response = client.get_account(
        acct_id, fields=tda.client.Client.Account.Fields.POSITIONS
    )
    summary = json.loads(response.content)
    quantity = 0
    positions = summary["securitiesAccount"]["positions"]
    for position in positions:
        if position["instrument"]["symbol"] == symbol:
            quantity = position["longQuantity"]
    return float(quantity)


def get_existing_stc_orders(client, acct_id: str, symbol_to_match: str):
    """Returns a list of existing single-leg STC orders for the given symbol.
    This library is not currently designed to work with multi-leg (complex) orders"""
    response = client.get_account(
        acct_id, fields=tda.client.Client.Account.Fields.ORDERS
    )
    summary = json.loads(response.content)
    order_ids = []
    orders = summary["securitiesAccount"]["orderStrategies"]
    for order in orders:
        # examine active orders
        if order["status"] == "WORKING" or order["status"] == "QUEUED":
            if len(order["orderLegCollection"]) == 1:  # no multi-leg orders
                instruct = order["orderLegCollection"][0]["instruction"]
                symbol = order["orderLegCollection"][0]["instrument"]["symbol"]
                if instruct == "SELL_TO_CLOSE" and symbol == symbol_to_match:
                    order_ids.append(str(order["orderId"]))
    return order_ids


def validate_user_settings(usr_settings: dict):
    """Raises an error for invalid inputs or sends a warning message to std.err"""

    try:
        for key, val in usr_settings.items():
            assert not isinstance(val, bool)
            assert isinstance(val, float) or isinstance(val, int)
    except AssertionError:
        msg = f"Illegal value type. Check configuration values"
        raise TypeError(msg) from None

    try:
        for key, val in usr_settings.items():
            if key == "max_ord_val":
                assert val > 0
            elif key == "SL_percent":
                assert 0 <= val < 1
            else:
                assert val >= 0
    except AssertionError:
        msg = "Please check order guideline values"
        raise ValueError(msg) from None

    if usr_settings["max_ord_val"] < 500:
        msg1 = "Maximum order value is less than $500.\n"
        msg2 = (
            "This is too small for some orders and may result in failure to purchase\n"
        )
        sys.stderr.write(msg1 + msg2)

    if usr_settings["buy_limit_percent"] >= 0.20:
        msg = f"Buy limit is {usr_settings['buy_limit_percent']}. Is that too risky?\n"
        sys.stderr.write(msg)

    if usr_settings["SL_percent"] >= 0.30:
        msg = f"SL percent is {usr_settings['SL_percent']}. Is that too risky?\n"
        sys.stderr.write(msg)

    if usr_settings["SL_percent"] <= 0.10:
        msg = f"SL percent is {usr_settings['SL_percent']}. Is that too low?\n"
        sys.stderr.write(msg)
