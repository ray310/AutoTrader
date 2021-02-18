import pytest
import datetime
import src.validate_params as vp

ORD_PARAMS = {
    "instruction": "BTO",
    "ticker": "INTC",
    "strike_price": "50.5",
    "contract_type": "C",
    "expiration": "12/31",
    "contract_price": "0.45",
    "comments": None,
}

USR_SETTINGS = {
    "max_ord_val": 500,
    "high_risk_ord_value": 300,
    "buy_limit_percent": 0.04,
    "SL_percent": 0.2,
}


def test_valid_params():
    """Valid params should return True """
    assert vp.validate_params(ORD_PARAMS) is True


def test_empty_dictionary():
    empty_dict = {}
    assert vp.validate_params(empty_dict) is False


def test_validate_params_invalid_expiration_date(monkeypatch):
    """Invalid expiration date should return False. is_expiration_valid() function is
    fully tested in a separate test script"""

    def mock_is_expiration_valid(expiration):
        return False

    monkeypatch.setattr(vp, "is_expiration_valid", mock_is_expiration_valid)
    assert vp.validate_params(ORD_PARAMS) is False


def test_validate_params_valid_instruction(monkeypatch):
    """Valid instructions should return True"""

    def mock_is_expiration_valid(expiration):
        return True

    monkeypatch.setattr(vp, "is_expiration_valid", mock_is_expiration_valid)
    good_instructions = ["BTO", "STC"]
    for good in good_instructions:
        monkeypatch.setitem(ORD_PARAMS, "instruction", good)
        assert vp.validate_params(ORD_PARAMS) is True


def test_validate_params_extra_chars_instruction(monkeypatch):
    """Permutation of BTO and STC with an extra character return False"""
    import itertools

    # check for permutations of valid instruction and extra chars
    prefixes = ["BTO", "STC", "B", "C", "S", "T", "/"]
    extra_char_prefix = ["".join(x) for x in itertools.permutations(prefixes, 2)]
    for prefix in extra_char_prefix:
        monkeypatch.setitem(ORD_PARAMS, "instruction", prefix)
        assert vp.validate_params(ORD_PARAMS) is False


def test_validate_params_lower_case_instruction(monkeypatch):
    """ BTO and STC instruction must be capitalized or return False.
    Combinations of letters in BTO and STC return False unless BTO and STC
    """
    import itertools

    valid_instructions = ["BTO", "STC"]
    letters = []
    for instruction in valid_instructions:
        letters.extend(list(instruction.upper() + instruction.lower()))
    chars = set(letters)  # to remove duplicates
    cart_product = ["".join(x) for x in itertools.product(chars, repeat=3)]
    invalid_cart_product = [x for x in cart_product if x != "BTO" and x != "STC"]
    for combo in invalid_cart_product:
        monkeypatch.setitem(ORD_PARAMS, "instruction", combo)
        assert vp.validate_params(ORD_PARAMS) is False


def test_validate_params_bad_instruction(monkeypatch):
    """Valid instruction should return True"""
    bad_instructions = [
        "",
        "/",
        "C",
        "P",
        "INTC",
        34,
        2.1,
        None,
        False,
        True,
        (),
        [],
        {},
        ["BTO"],
        ("BTO",),
        {"instruction", "BTO"},
    ]
    for bad in bad_instructions:
        monkeypatch.setitem(ORD_PARAMS, "instruction", bad)
        assert vp.validate_params(ORD_PARAMS) is False


def test_validate_params_good_tickers(monkeypatch):
    """Valid tickers should return True """

    def mock_is_expiration_valid(expiration):
        return True

    monkeypatch.setattr(vp, "is_expiration_valid", mock_is_expiration_valid)
    tickers = ["A", "AB", "ABC", "ABCD", "ABCDE"]
    for tckr in tickers:
        monkeypatch.setitem(ORD_PARAMS, "ticker", tckr)
        assert vp.validate_params(ORD_PARAMS) is True


def test_validate_params_bad_tickers(monkeypatch):
    """Valid tickers should return True """
    tickers = [
        "",
        "a",
        "abc",
        "ABCDEF",
        None,
        True,
        False,
        2.1,
        3,
        (),
        [],
        {},
        ["ABC"],
        ("ABC",),
        {"ticker": "ABC"},
    ]
    for tckr in tickers:
        monkeypatch.setitem(ORD_PARAMS, "ticker", tckr)
        assert vp.validate_params(ORD_PARAMS) is False


def test_validate_params_valid_strike(monkeypatch):
    """Valid strike price should return True"""

    def mock_is_expiration_valid(expiration):
        return True

    monkeypatch.setattr(vp, "is_expiration_valid", mock_is_expiration_valid)
    good_strike = ["1", "12", "123", "1234", "12345", "12345.5", "12345.50"]
    for good in good_strike:
        monkeypatch.setitem(ORD_PARAMS, "strike_price", good)
        assert vp.validate_params(ORD_PARAMS) is True


def test_validate_params_bad_strike(monkeypatch):
    """Invalid strike price should return False"""
    bad_strike = [
        "",
        "-12",
        "0",
        ".5",
        "20.51",
        "20.1",
        "20.05",
        "20.005",
        "123456",
        "123456.50",
        "12.z",
        "C",
        "P",
        [],
        (),
        {},
        ["34"],
        ("34",),
        {"strike_price": "34"},
    ]
    for bad in bad_strike:
        monkeypatch.setitem(ORD_PARAMS, "strike_price", bad)
        assert vp.validate_params(ORD_PARAMS) is False


def test_is_expiration_valid_good_dates(monkeypatch):
    """ Valid expiration dates return True"""

    def mock_expired(dt_obj):
        return False

    monkeypatch.setattr(vp, "expired", mock_expired)
    expirations = [
        "1/1",
        "12/12",
        "12/31",
        "01/01/22",
        "01/01/2022",
        "1/1/22",
        "1/1/2022",
    ]
    for date in expirations:
        assert vp.is_expiration_valid(date) is True


def test_is_expiration_valid_bad_dates(monkeypatch):
    """ Bad expiration dates return False"""
    future_year = datetime.datetime.today().year + 4  # 4 years in future not allowed
    expirations = [
        "13/1",
        "12/33",
        "2/30",
        "01/01/2",
        "01/01/202",
        "1/1/",
        "1/1/00",
        "1/1/20224",
        "1/1/" + str(future_year),
        "",
        "/",
        "/2022",
        "1/1/1/1",
        "01012023",
        "01-01",
        "3 Jan",
        10122022,
        ("1/1",),
        ["1/1"],
        {"expiration": "01/01"},
        "@",
        None,
        True,
        False,
    ]
    for date in expirations:
        assert vp.is_expiration_valid(date) is False


def test_is_expiration_valid_previous_date(monkeypatch):
    """ Date past expiration returns False"""

    def mock_expired(dt_obj):
        return True

    monkeypatch.setattr(vp, "expired", mock_expired)
    assert vp.is_expiration_valid("1/1") is False


def test_expired():
    """Test expired function"""
    future = datetime.datetime.today() + datetime.timedelta(days=1)
    past = datetime.datetime.today() - datetime.timedelta(days=1)
    assert vp.expired(future) is False
    assert vp.expired(past) is True


def test_validate_params_valid_contract_type(monkeypatch):
    """Valid contract type should return True"""

    def mock_is_expiration_valid(expiration):
        return True

    monkeypatch.setattr(vp, "is_expiration_valid", mock_is_expiration_valid)
    good_contract = ["C", "P"]
    for good in good_contract:
        monkeypatch.setitem(ORD_PARAMS, "contract_type", good)
        assert vp.validate_params(ORD_PARAMS) is True


def test_validate_params_bad_contract_type(monkeypatch):
    """Invalid contract type should return False"""
    bad_contract = [
        "",
        "c",
        "p",
        "@",
        2,
        "2",
        "Z",
        True,
        False,
        None,
        2.1,
        (),
        [],
        {},
        ("C",),
        ["C"],
        {"contract_type": "C"},
    ]
    for bad in bad_contract:
        monkeypatch.setitem(ORD_PARAMS, "contract_type", bad)
        assert vp.validate_params(ORD_PARAMS) is False


def test_validate_params_valid_contract_price(monkeypatch):
    """Valid contract price returns True (positive number under 1000)"""

    def mock_is_expiration_valid(expiration):
        return True

    monkeypatch.setattr(vp, "is_expiration_valid", mock_is_expiration_valid)
    prices = [
        ".01",
        ".12",
        "0.12",
        "1.23",
        "12.34",
        "123.45",
        ".1",
        "0.1",
        "12.3",
        "123.4",
    ]
    for price in prices:
        monkeypatch.setitem(ORD_PARAMS, "contract_price", price)
        assert vp.validate_params(ORD_PARAMS) is True


def test_validate_params_bad_contract_price(monkeypatch):
    """Invalid contract prices return False"""
    prices = [
        "",
        "1234",
        "-1",
        "0",
        None,
        True,
        False,
        "@",
        "C",
        "p",
        (),
        [],
        {},
        ("34",),
        ["34"],
        {"contract_price": "34"},
    ]
    for price in prices:
        monkeypatch.setitem(ORD_PARAMS, "contract_price", price)
        assert vp.validate_params(ORD_PARAMS) is False


def test_validate_user_inputs_no_warning_or_exception(monkeypatch):
    """ Value range of user inputs issues no warning or exception"""
    safe_max_order = [500, 500.01, 1000, 1000.01, 10000, 10000.01]
    for max_ord in safe_max_order:
        monkeypatch.setitem(USR_SETTINGS, "max_ord_val", max_ord)
        assert vp.validate_user_settings(USR_SETTINGS) is None

    safe_buy_limit = [0, 0.0, 0.1, 0.10, 0.10, 0.19, 0.190, 0.190, 0.1999, 0.1999]
    for bl in safe_buy_limit:
        monkeypatch.setitem(USR_SETTINGS, "buy_limit_percent", bl)
        assert vp.validate_user_settings(USR_SETTINGS) is None

    safe_sl_percent = [0.11, 0.11, 0.2, 0.20, 0.20, 0.29, 0.29, 0.2999, 0.2999]
    for sl in safe_sl_percent:
        monkeypatch.setitem(USR_SETTINGS, "SL_percent", sl)
        assert vp.validate_user_settings(USR_SETTINGS) is None


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
            vp.validate_user_settings(USR_SETTINGS)


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
            vp.validate_user_settings(USR_SETTINGS)


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
            vp.validate_user_settings(USR_SETTINGS)


def test_validate_user_inputs_raise_value_error_max(monkeypatch):
    """ Raise ValueError Exceptions"""
    except_max_order = [-100, -100.0, -100.0, 0, 0.0]
    for max_ord in except_max_order:
        monkeypatch.setitem(USR_SETTINGS, "max_ord_val", max_ord)
        with pytest.raises(ValueError):
            vp.validate_user_settings(USR_SETTINGS)


def test_validate_user_inputs_raise_value_error_buy_limit(monkeypatch):
    except_buy_limit = [-100, -100.0, -100.0]
    for bl in except_buy_limit:
        monkeypatch.setitem(USR_SETTINGS, "buy_limit_percent", bl)
        with pytest.raises(ValueError):
            vp.validate_user_settings(USR_SETTINGS)


def test_validate_user_inputs_raise_value_error_sl(monkeypatch):
    except_sl_percent = [-5, -1.0, -1, 1, 1.00, 1.01, 5]
    for sl in except_sl_percent:
        monkeypatch.setitem(USR_SETTINGS, "SL_percent", sl)
        with pytest.raises(ValueError):
            vp.validate_user_settings(USR_SETTINGS)


def test_validate_user_inputs_warn_low_max(monkeypatch, capsys):
    warn_max_order = [0.01, 250, 499.99]
    msg1 = "Maximum order value is less than $500.\n"
    msg2 = "This is too small for some orders and may result in failure to purchase\n"
    for max_ord in warn_max_order:
        monkeypatch.setitem(USR_SETTINGS, "max_ord_val", max_ord)
        vp.validate_user_settings(USR_SETTINGS)
        captured = capsys.readouterr()
        assert captured.err == msg1 + msg2


def test_validate_user_inputs_warn_high_buy_limit(monkeypatch, capsys):
    warn_buy_limit = [0.20, 0.2, 1, 1.0, 5, 5.0]
    for bl in warn_buy_limit:
        monkeypatch.setitem(USR_SETTINGS, "buy_limit_percent", bl)
        msg = f"Buy limit is {USR_SETTINGS['buy_limit_percent']}. Is that too risky?\n"
        vp.validate_user_settings(USR_SETTINGS)
        captured = capsys.readouterr()
        assert captured.err == msg


def test_validate_user_inputs_warn_high_sl(monkeypatch, capsys):
    warn_sl_percent = [0.30, 0.3, 0.99]
    for sl in warn_sl_percent:
        monkeypatch.setitem(USR_SETTINGS, "SL_percent", sl)
        msg = f"SL percent is {USR_SETTINGS['SL_percent']}. Is that too risky?\n"
        vp.validate_user_settings(USR_SETTINGS)
        captured = capsys.readouterr()
        assert captured.err == msg


def test_validate_user_inputs_warn_low_sl(monkeypatch, capsys):
    warn_sl_percent = [0, 0.01, 0.1]
    for sl in warn_sl_percent:
        monkeypatch.setitem(USR_SETTINGS, "SL_percent", sl)
        msg = f"SL percent is {USR_SETTINGS['SL_percent']}. Is that too low?\n"
        vp.validate_user_settings(USR_SETTINGS)
        captured = capsys.readouterr()
        assert captured.err == msg
