"""Tests for ameritrade_orders.py"""
import pytest
import datetime
import tda
import auto_trader_client.src.ameritrade_orders as am

VALID_ORD = {
    "instruction": "BTO",
    "ticker": "TSLA",
    "strike_price": "520",
    "contract_type": "P",
    "expiration": datetime.datetime(2021, 3, 5, 0, 0),
    "contract_price": 1.00,
    "comments": None,
}
USR_SETTINGS = {"max_ord_val": 500, "buy_limit_percent": 0.04, "SL_percent": 0.2}


def test_authenticate_tda_account_token(monkeypatch):
    """Testing authentication flow with valid token"""

    def mock_client_from_token_file(token_path, api_key):
        return tda.client.Client

    monkeypatch.setattr(tda.auth, "client_from_token_file", mock_client_from_token_file)
    assert am.authenticate_tda_account("path.json", "key", "uri") == tda.client.Client


def test_build_stc_market_order():
    """Testing for changes to tda-api package, Note that fractional orders can
    be constructed even if TDA API may reject them"""
    order_qty = [0.5, 1, 100000]
    for qty in order_qty:
        order = am.build_stc_market_order(VALID_ORD, qty)
        assert isinstance(order, tda.orders.generic.OrderBuilder)

    with pytest.raises(ValueError):
        am.build_stc_market_order(VALID_ORD, 0)


def test_calc_buy_order():
    """Returns rounded-down integer"""
    assert am.calc_buy_order_quantity(price=1, max_ord_val=100, limit_percent=0) == 1
    assert am.calc_buy_order_quantity(price=1, max_ord_val=100, limit_percent=0.1) == 0
    ret_val = am.calc_buy_order_quantity(price=1, max_ord_val=100, limit_percent=0)
    assert isinstance(ret_val, int)


def test_validate_user_inputs_no_warning_or_exception(monkeypatch):
    """ Value range of user inputs issues no warning or exception"""
    safe_max_order = [500, 500.01, 1000, 1000.01, 10000, 10000.01]
    for max_ord in safe_max_order:
        monkeypatch.setitem(USR_SETTINGS, "max_ord_val", max_ord)
        assert am.validate_user_settings(USR_SETTINGS) is None

    safe_buy_limit = [0, 0.0, 0.1, 0.10, 0.10, 0.19, 0.190, 0.190, 0.1999, 0.1999]
    for bl in safe_buy_limit:
        monkeypatch.setitem(USR_SETTINGS, "buy_limit_percent", bl)
        assert am.validate_user_settings(USR_SETTINGS) is None

    safe_sl_percent = [0.11, 0.11, 0.2, 0.20, 0.20, 0.29, 0.29, 0.2999, 0.2999]
    for sl in safe_sl_percent:
        monkeypatch.setitem(USR_SETTINGS, "SL_percent", sl)
        assert am.validate_user_settings(USR_SETTINGS) is None


def test_validate_user_inputs_raise_type_error_max(monkeypatch):
    """ Raise TypeError Exceptions"""
    except_max_order = [
        "500",
        "500.01",
        (500,),
        [500],
        {"max_ord_val": 500},
        True,
        False,
        None,
        USR_SETTINGS,
    ]
    for max_ord in except_max_order:
        monkeypatch.setitem(USR_SETTINGS, "max_ord_val", max_ord)
        with pytest.raises(TypeError):
            am.validate_user_settings(USR_SETTINGS)


def test_validate_user_inputs_raise_type_error_buy_limit(monkeypatch):
    except_buy_limit = [
        "0.1",
        ".1",
        (0.1,),
        [0.1],
        {"buy_limit_percent": 0.1},
        True,
        False,
        None,
        USR_SETTINGS,
    ]
    for bl in except_buy_limit:
        monkeypatch.setitem(USR_SETTINGS, "buy_limit_percent", bl)
        with pytest.raises(TypeError):
            am.validate_user_settings(USR_SETTINGS)


def test_validate_user_inputs_raise_type_error_sl(monkeypatch):
    except_sl_percent = [
        "0.1",
        ".1",
        (0.1,),
        [0.1],
        {"SL_percent": 0.1},
        True,
        False,
        None,
        USR_SETTINGS,
    ]
    for sl in except_sl_percent:
        monkeypatch.setitem(USR_SETTINGS, "SL_percent", sl)
        with pytest.raises(TypeError):
            am.validate_user_settings(USR_SETTINGS)


def test_validate_user_inputs_raise_value_error_max(monkeypatch):
    """ Raise ValueError Exceptions"""
    except_max_order = [-100, -100.0, -100.0, 0, 0.0]
    for max_ord in except_max_order:
        monkeypatch.setitem(USR_SETTINGS, "max_ord_val", max_ord)
        with pytest.raises(ValueError):
            am.validate_user_settings(USR_SETTINGS)


def test_validate_user_inputs_raise_value_error_buy_limit(monkeypatch):
    except_buy_limit = [-100, -100.0, -100.0]
    for bl in except_buy_limit:
        monkeypatch.setitem(USR_SETTINGS, "buy_limit_percent", bl)
        with pytest.raises(ValueError):
            am.validate_user_settings(USR_SETTINGS)


def test_validate_user_inputs_raise_value_error_sl(monkeypatch):
    except_sl_percent = [-5, -1.0, -1, 1, 1.00, 1.01, 5]
    for sl in except_sl_percent:
        monkeypatch.setitem(USR_SETTINGS, "SL_percent", sl)
        with pytest.raises(ValueError):
            am.validate_user_settings(USR_SETTINGS)


def test_validate_user_inputs_warn_low_max(monkeypatch, capsys):
    warn_max_order = [0.01, 250, 499.99]
    msg1 = "Maximum order value is less than $500.\n"
    msg2 = "This is too small for some orders and may result in failure to purchase\n"
    for max_ord in warn_max_order:
        monkeypatch.setitem(USR_SETTINGS, "max_ord_val", max_ord)
        am.validate_user_settings(USR_SETTINGS)
        captured = capsys.readouterr()
        assert captured.err == msg1 + msg2


def test_validate_user_inputs_warn_high_buy_limit(monkeypatch, capsys):
    warn_buy_limit = [0.20, 0.2, 1, 1.0, 5, 5.0]
    for bl in warn_buy_limit:
        monkeypatch.setitem(USR_SETTINGS, "buy_limit_percent", bl)
        msg = f"Buy limit is {USR_SETTINGS['buy_limit_percent']}. Is that too risky?\n"
        am.validate_user_settings(USR_SETTINGS)
        captured = capsys.readouterr()
        assert captured.err == msg


def test_validate_user_inputs_warn_high_sl(monkeypatch, capsys):
    warn_sl_percent = [0.30, 0.3, 0.99]
    for sl in warn_sl_percent:
        monkeypatch.setitem(USR_SETTINGS, "SL_percent", sl)
        msg = f"SL percent is {USR_SETTINGS['SL_percent']}. Is that too risky?\n"
        am.validate_user_settings(USR_SETTINGS)
        captured = capsys.readouterr()
        assert captured.err == msg


def test_validate_user_inputs_warn_low_sl(monkeypatch, capsys):
    warn_sl_percent = [0, 0.01, 0.1]
    for sl in warn_sl_percent:
        monkeypatch.setitem(USR_SETTINGS, "SL_percent", sl)
        msg = f"SL percent is {USR_SETTINGS['SL_percent']}. Is that too low?\n"
        am.validate_user_settings(USR_SETTINGS)
        captured = capsys.readouterr()
        assert captured.err == msg
