"""Tests for ameritrade_orders.py"""
import pytest
import datetime
import math
import copy
import tda
import src.ameritrade_orders as am

VALID_ORD_INPUT = {
    "instruction": "BTO",
    "ticker": "TSLA",
    "strike_price": "520",
    "contract_type": "P",
    "expiration": datetime.datetime(2021, 3, 5, 0, 0),
    "contract_price": 1.00,
    "comments": None,
    "flags": {"SL": None, "risk_level": None, "reduce": None},
}

ORD_JSON_DICT = {
    "session": "NORMAL",
    "duration": "DAY",
    "orderType": "LIMIT",
    "complexOrderStrategyType": "NONE",
    "quantity": 1.0,
    "filledQuantity": 0.0,
    "remainingQuantity": 0.0,
    "requestedDestination": "AUTO",
    "destinationLinkName": "AutoRoute",
    "price": 3.26,
    "orderLegCollection": [
        {
            "orderLegType": "OPTION",
            "legId": 1,
            "instrument": {
                "assetType": "OPTION",
                "cusip": "0TSLA.O510520000",
                "symbol": "TSLA_030521P520",
                "description": "TSLA Mar 05 2021 520.0 Put",
                "underlyingSymbol": "TSLA",
            },
            "instruction": "BUY_TO_OPEN",
            "positionEffect": "OPENING",
            "quantity": 1.0,
        }
    ],
    "orderStrategyType": "TRIGGER",
    "orderId": 1234567890,
    "cancelable": False,
    "editable": False,
    "status": "CANCELED",
    "enteredTime": "2021-01-10T06:54:32+0000",
    "closeTime": "2021-01-10T07:00:08+0000",
    "tag": "app_name",
    "accountId": 123456789,
    "childOrderStrategies": [
        {
            "session": "NORMAL",
            "duration": "GOOD_TILL_CANCEL",
            "orderType": "STOP",
            "cancelTime": "2021-03-05",
            "complexOrderStrategyType": "NONE",
            "quantity": 1.0,
            "filledQuantity": 0.0,
            "remainingQuantity": 0.0,
            "requestedDestination": "AUTO",
            "destinationLinkName": "AutoRoute",
            "stopPrice": 1.00,
            "orderLegCollection": [
                {
                    "orderLegType": "OPTION",
                    "legId": 1,
                    "instrument": {
                        "assetType": "OPTION",
                        "cusip": "0TSLA.O510520000",
                        "symbol": "TSLA_030521P520",
                        "description": "TSLA Mar 05 2021 520.0 Put",
                        "underlyingSymbol": "TSLA",
                    },
                    "instruction": "SELL_TO_CLOSE",
                    "positionEffect": "CLOSING",
                    "quantity": 1.0,
                }
            ],
            "orderStrategyType": "SINGLE",
            "orderId": 1234567891,
            "cancelable": False,
            "editable": False,
            "status": "CANCELED",
            "enteredTime": "2021-01-10T06:54:32+0000",
            "closeTime": "2021-01-10T07:00:08+0000",
            "tag": "app_name",
            "accountId": 1234567890,
        }
    ],
}

POSITIONS = {
    "securitiesAccount": {
        "type": "CASH",
        "accountId": "1234567890",
        "roundTrips": 0,
        "isDayTrader": False,
        "isClosingOnlyRestricted": False,
        "positions": [
            {
                "shortQuantity": 0.0,
                "averagePrice": 0.6566,
                "currentDayProfitLoss": -5.5,
                "currentDayProfitLossPercentage": -9.02,
                "longQuantity": 1.0,
                "settledLongQuantity": 1.0,
                "settledShortQuantity": 0.0,
                "instrument": {
                    "assetType": "OPTION",
                    "cusip": "0SPY..P110300000",
                    "symbol": "SPY_040121P300",
                    "description": "SPY Apr 01 2021 300.0 Put",
                    "type": "VANILLA",
                    "putCall": "PUT",
                    "underlyingSymbol": "SPY",
                },
                "marketValue": 55.5,
                "maintenanceRequirement": 0.0,
            },
            {
                "shortQuantity": 0.0,
                "averagePrice": 1.0,
                "currentDayProfitLoss": 0.0,
                "currentDayProfitLossPercentage": 0.0,
                "longQuantity": 27.0,
                "settledLongQuantity": 27.0,
                "settledShortQuantity": 0.0,
                "instrument": {
                    "assetType": "OPTION",
                    "cusip": "0SPY..O310380000",
                    "symbol": "SPY_030321P380",
                    "description": "SPY Mar 03 2021 380.0 Put",
                    "type": "VANILLA",
                    "putCall": "PUT",
                    "underlyingSymbol": "SPY",
                },
                "marketValue": 2700.0,
                "maintenanceRequirement": 0.0,
            },
        ],
    }
}


def test_authenticate_tda_account_token(monkeypatch):
    """Testing authentication flow with valid token"""

    def mock_client_from_token_file(token_path, api_key):
        return tda.client.Client

    monkeypatch.setattr(tda.auth, "client_from_token_file", mock_client_from_token_file)
    assert am.authenticate_tda_account("path.json", "key", "uri") == tda.client.Client


def test_calc_buy_order():
    """Returns rounded-down integer"""
    ret_val = am.calc_buy_order_quantity(price=1, ord_val=100, limit_percent=0)
    assert isinstance(ret_val, int)
    assert am.calc_buy_order_quantity(price=1, ord_val=100, limit_percent=0) == 1
    assert am.calc_buy_order_quantity(price=1, ord_val=100, limit_percent=0.1) == 0


def test_get_position_quant(monkeypatch):
    """Returns long position or None if no long position"""
    # mock call to API and returned object
    class MockResponse:
        @staticmethod
        def json():
            return POSITIONS

    def mock_get_account(acct_id, fields):
        return MockResponse

    client = tda.client.Client
    monkeypatch.setattr(client, "get_account", mock_get_account)
    acct_num = "1234567890"

    symbol = "SPY_030321P380"
    qty = am.get_position_quant(client, acct_num, symbol)
    assert math.isclose(qty, 27.0)

    non_existent_symbol = "AAPL_030321C20"
    assert am.get_position_quant(client, acct_num, non_existent_symbol) is None


def test_get_existing_stc_orders_valid(monkeypatch):
    """Orders containing valid STC orders return order ids """
    # prepare test orders
    orders = [copy.deepcopy(ORD_JSON_DICT) for i in range(2)]

    # Active STC order, orderId should be returned
    orders[0]["orderLegCollection"][0]["instruction"] = "SELL_TO_CLOSE"
    orders[0]["status"] = "WORKING"
    orders[0]["orderId"] = 1

    # Filled BTO with an active STC child order. orderId should be returned
    orders[1]["orderLegCollection"][0]["instruction"] = "BUY_TO_OPEN"
    orders[1]["status"] = "FILLED"
    orders[1]["orderId"] = 2
    orders[1]["childOrderStrategies"][0]["status"] = "QUEUED"
    orders[1]["childOrderStrategies"][0]["orderId"] = 3

    # mock call to API and returned object
    class MockResponse:
        @staticmethod
        def json():
            return orders

    def mock_get_orders_by_query(from_entered_datetime, statuses):
        return MockResponse

    client = tda.client.Client
    monkeypatch.setattr(client, "get_orders_by_query", mock_get_orders_by_query)

    symbol = "TSLA_030521P520"
    assert am.get_existing_stc_orders(client, symbol) == ["1", "3"]


def test_get_existing_stc_orders_invalid(monkeypatch):
    """ Orders not containing valid STC order return empty list"""
    # prepare test orders
    orders = [copy.deepcopy(ORD_JSON_DICT) for i in range(3)]

    # Active STC order, orderId should be returned
    orders[0]["orderLegCollection"][0]["instruction"] = "SELL_TO_CLOSE"
    orders[0]["status"] = "REJECTED"
    orders[0]["orderId"] = 1

    # Filled BTO with an active STC child order. orderId should be returned
    orders[1]["orderLegCollection"][0]["instruction"] = "BUY_TO_OPEN"
    orders[1]["status"] = "FILLED"
    orders[1]["orderId"] = 2
    orders[1]["childOrderStrategies"][0]["status"] = "CANCELLED"
    orders[1]["childOrderStrategies"][0]["orderId"] = 3

    # mock call to API and returned object
    class MockResponse:
        @staticmethod
        def json():
            return orders

    def mock_get_orders_by_query(from_entered_datetime, statuses):
        return MockResponse

    client = tda.client.Client
    symbol = "TSLA_030521P520"
    monkeypatch.setattr(client, "get_orders_by_query", mock_get_orders_by_query)
    assert am.get_existing_stc_orders(client, symbol) == []


def test_check_stc_order_valid():
    """STC orders should return order is number as a string"""
    order = copy.deepcopy(ORD_JSON_DICT)
    symbol = "TSLA_030521P520"
    order["orderLegCollection"][0]["instruction"] = "SELL_TO_CLOSE"
    statuses = ["WORKING", "QUEUED", "ACCEPTED"]
    for status in statuses:
        order["status"] = status
        assert am.check_stc_order(order, symbol) == "1234567890"


def test_check_stc_order_invalid():
    """Invalid orders should return None"""
    order = copy.deepcopy(ORD_JSON_DICT)
    symbol = "TSLA_030521P520"

    # BTO returns None
    order["orderLegCollection"][0]["instruction"] = "BUY_TO_OPEN"
    statuses = ["WORKING", "QUEUED", "ACCEPTED"]
    for status in statuses:
        order["status"] = status
        assert am.check_stc_order(order, symbol) is None

    # STC returns None because of status
    order["orderLegCollection"][0]["instruction"] = "SELL_TO_CLOSE"
    statuses = ["REJECTED", "CANCELED", "FILLED"]
    for status in statuses:
        order["status"] = status
        assert am.check_stc_order(order, symbol) is None


def test_calc_position_reduction():
    """Should correctly round up sell part of sell/keep split"""
    qty_percent_split = [
        (1, 0.10, (1, 0)),
        (5, 0.405, (3, 2)),
        (10, 0.50, (5, 5)),
        (10, 0.75, (8, 2)),
    ]
    for tup in qty_percent_split:
        assert am.calc_position_reduction(tup[0], tup[1]) == tup[2]


def test_build_stc_market_order():
    """Testing for changes to tda-api package, Note that fractional orders can
    be constructed even if TDA API may reject them"""
    order_qty = [0.5, 1, 100000]
    for qty in order_qty:
        order = am.build_stc_market_order(VALID_ORD_INPUT, qty)
        assert isinstance(order, tda.orders.generic.OrderBuilder)

    with pytest.raises(ValueError):
        am.build_stc_market_order(VALID_ORD_INPUT, 0)


def test_build_stc_stop_market():
    """Returned order should be stop (stop-market), good until canceled and correctly
    round floats"""
    symbol = "TSLA_030521P520"
    qty = 3
    stop_price_truncated = [(3.3451, 3.35), (0.1449, 0.14)]
    for prices in stop_price_truncated:
        order = am.build_stc_stop_market(symbol, qty, stop_price=prices[0])
        assert order._duration == "GOOD_TILL_CANCEL"
        assert order._orderType == "STOP"
        assert math.isclose(float(order._stopPrice), prices[1])
