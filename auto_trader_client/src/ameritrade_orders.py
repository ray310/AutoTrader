"""Functions needed to execute TD Ameritrade orders"""

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
    with open(TD_AUTH_PARAMS_PATH) as fp:
        td_auth_params = json.load(fp)
    uri = td_auth_params[TD_DICT_KEY_URI]
    api_key = td_auth_params[TD_DICT_KEY_API]
    acct_num = td_auth_params[TD_DICT_KEY_ACCT]

    with open(ORD_SETTINGS_PATH) as fp:
        order_settings = json.load(fp)
    ord_value = order_settings[ORD_VAL_KEY]
    buy_limit_percent = order_settings[BUY_LIM_KEY]
    stop_loss_percent = order_settings[SL_KEY]

    # authenticate
    client = authenticate_tda_account(TD_TOKEN_PATH, api_key, uri)

    # generate and place order
    if ord_params["instruction"] == "BTO":
        ota_order = generate_bto_order(
            ord_params, ord_value, buy_limit_percent, stop_loss_percent
        )
        # place order. order_spec takes OrderBuilder obj
        response = client.place_order(acct_num, order_spec=ota_order)
        logging.info(response)
    elif ord_params["instruction"] == "STC":
        stc = generate_stc_order(client, acct_num, ord_params)
        if stc is not None:
            response = client.place_order(acct_num, order_spec=stc)
            logging.info(response)
    else:
        instr = ord_params["instruction"]
        logging.warning(f"Invalid order instruction: {instr}")


# creating more than one client_tests will likely cause issues with authentication
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


def generate_bto_order(
    ord_params: dict, ord_val: float, limit_percent: float, stop_loss_percent: float
):
    """ Prepares and returns one-trigger another order
    with BTO limit and STC stop-market"""
    # prepare BTO inputs
    qty = calc_order_quantity(ord_params["contract_price"], ord_val, limit_percent)
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


def generate_stc_order(client, acct_id: str, ord_params: dict):
    """ Returns STC market order is there is a long position for the given option,
    else returns None"""
    option_symbol = build_option_symbol(ord_params)
    qty = get_position_quant(client, acct_id, option_symbol)
    if qty > 0:
        stc = tda.orders.options.option_sell_to_close_market(option_symbol, qty)
        return stc
    else:
        return None


def calc_order_quantity(
    price: float, ord_val: float, limit_percent: float, lot_size=100
):
    """Return the order quantity """
    lot_value = price * lot_size * (1 + limit_percent)
    quantity = int(ord_val / lot_value)  # int() rounds down
    return quantity


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
