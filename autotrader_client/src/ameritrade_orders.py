"""Functions needed to execute TD Ameritrade orders"""

import sys
import tda
import tda.orders.options
import json
import logging
import datetime
import math
from src.client_settings import (
    TD_TOKEN_PATH,
    TD_AUTH_PARAMS_PATH,
    TD_DICT_KEY_API,
    TD_DICT_KEY_URI,
    TD_DICT_KEY_ACCT,
    ORD_SETTINGS_PATH,
    MAX_ORD_VAL_KEY,
    RISKY_ORD_VAL_KEY,
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
    # max_ord_val is max $ value of order e.g. 500.00
    # high_risk_ord_value is the order value for higher risk orders
    usr_set = {
        "max_ord_val": order_settings[MAX_ORD_VAL_KEY],
        "high_risk_ord_value": order_settings[RISKY_ORD_VAL_KEY],
        "buy_limit_percent": order_settings[BUY_LIM_KEY],
        "SL_percent": order_settings[SL_KEY],
    }

    # check user inputs
    validate_user_settings(usr_set)

    # authenticate
    client = authenticate_tda_account(TD_TOKEN_PATH, td_acct["api_key"], td_acct["uri"])

    # generate and place order
    if ord_params["instruction"] == "BTO":
        # set order value based on risk level
        if ord_params["flags"]["risk_level"] == "high risk":
            order_value = usr_set["high_risk_ord_value"]
        else:
            order_value = usr_set["max_ord_value"]

        buy_qty = calc_buy_order_quantity(
            ord_params["contract_price"], order_value, usr_set["buy_limit_percent"],
        )
        if buy_qty >= 1:
            if ord_params["flags"]["SL"]:
                suggested_sl = float(ord_params["flags"]["SL"])
                suggested_sl_percent = calc_sl_percentage(
                    ord_params["contract_price"], suggested_sl
                )
                # use more conservative of two
                if suggested_sl_percent < usr_set["SL_percent"]:
                    sl_percent = suggested_sl_percent
                else:
                    sl_percent = usr_set["SL_percent"]

            ota_order = build_bto_order_w_stop_loss(
                ord_params, buy_qty, usr_set["buy_limit_percent"], sl_percent,
            )
            response = client.place_order(td_acct["acct_num"], order_spec=ota_order)
            logging.info(response.content)
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
            existing_stc_ids = get_existing_stc_orders(client, symbol)
            if len(existing_stc_ids) > 0:
                for ord_id in existing_stc_ids:
                    response = client.cancel_order(ord_id, td_acct["acct_num"])
                    logging.info(response.content)
            if ord_params["flags"]["reduce"]:
                sell_qty, keep_qty = calc_reduction(position_qty, ord_params["flags"]["reduce"])
                stc = build_stc_market_order(ord_params, sell_qty)
                response = client.place_order(td_acct["acct_num"], order_spec=stc)
                logging.info(response.content)
                stc_stop = build_stc_stop_market(symbol, keep_qty, ord_params["contract_price"])  #TODO: needs to calculate stop price
                response = client.place_order(td_acct["acct_num"], order_spec=stc_stop)
                logging.info(response.content)
            else:
                stc = build_stc_market_order(ord_params, position_qty)
                response = client.place_order(td_acct["acct_num"], order_spec=stc)
                logging.info(response.content)
    else:
        instr = ord_params["instruction"]
        logging.warning(f"Invalid order instruction: {instr}")


# creating more than one client will likely cause issues with authentication
def authenticate_tda_account(token_path: str, api_key: str, redirect_uri: str):
    """Takes TDA app key and path to locally stored auth token and tries to
    authenticate. If unable to authenticate with token, performs backup authentication
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


def calc_reduction(pos_qty: int, string_percent: str):
    """Calculate the quantity that should be immediately sold and the quantity that
    should be held with an STC stop market in place. Returns sell / keep quantities"""
    reduce_per = (float(string_percent.replace("%", ""))) / 100
    sell_qty = math.ceil(pos_qty * reduce_per)
    keep_qty = pos_qty - sell_qty
    return sell_qty, keep_qty


def calc_buy_order_quantity(price: float, max_ord_val: float, limit_percent: float):
    """Returns the order quantity (int) for a buy order based on
    the option price, maximum order size, and buy limit percent  """
    lot_size = 100  # standard lot size value
    lot_value = price * lot_size * (1 + limit_percent)
    quantity = max_ord_val / lot_value
    return int(quantity)  # int() rounds down


def calc_sl_percentage(contract_price: float, sl_price: float):
    """Returns percentage difference from contract price to stop loss price"""
    return (contract_price - sl_price) / contract_price


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


def build_bto_order_w_stop_loss(
    ord_params: dict,
    qty: int,
    limit_percent: float,
    stop_loss_percent: float,
    kill_fill=True,
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
    if kill_fill:
        bto_lim.set_duration(tda.orders.common.Duration.FILL_OR_KILL)
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


def get_existing_stc_orders(client, symbol: str):
    """Returns a list of existing single-leg STC orders for the given symbol.
    This library is not currently designed to work with multi-leg (complex) orders"""
    now = datetime.datetime.utcnow()
    query_start = now - datetime.timedelta(hours=32)  # from up to previous trading day
    statuses = (
        tda.client.Client.Order.Status.FILLED,
        tda.client.Client.Order.Status.QUEUED,
        tda.client.Client.Order.Status.ACCEPTED,
        tda.client.Client.Order.Status.WORKING,
    )  # waiting for tda patch to implement multi-status check and speed up query time

    response = client.get_orders_by_query(
        from_entered_datetime=query_start, statuses=None
    )
    summary = json.loads(response.content)
    order_ids = []
    for order in summary:
        # examine active orders and their child orders
        if order["status"] in ["WORKING", "QUEUED", "ACCEPTED"]:
            if len(order["orderLegCollection"]) == 1:  # no multi-leg orders
                instruct = order["orderLegCollection"][0]["instruction"]
                ord_symbol = order["orderLegCollection"][0]["instrument"]["symbol"]
                if ord_symbol == symbol and instruct == "SELL_TO_CLOSE":
                    order_ids.append(str(order["orderId"]))
                elif ord_symbol == symbol and ["orderStrategyType"] == "TRIGGER":
                    child_order_id = check_child_stc_order(order, symbol)
                    if child_order_id:
                        order_ids.append(child_order_id)

        # if filled, check for open sell order with active status
        elif order["status"] == "FILLED" and order["orderStrategyType"] == "TRIGGER":
            child_order_id = check_child_stc_order(order, symbol)
            if child_order_id:
                order_ids.append(child_order_id)
    return order_ids


def check_child_stc_order(order, symbol):
    """Return order id if child order has STC order
    for input symbol, else return None"""
    # not currently handling conditional orders with more than one child order
    child = order["childOrderStrategies"][0]
    if child["status"] in ["WORKING", "QUEUED", "ACCEPTED"]:
        if len(child["orderLegCollection"]) == 1:  # no multi-leg orders
            instruct = child["orderLegCollection"][0]["instruction"]
            ord_symbol = child["orderLegCollection"][0]["instrument"]["symbol"]
            if ord_symbol == symbol and instruct == "SELL_TO_CLOSE":
                return str(child["orderId"])


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
