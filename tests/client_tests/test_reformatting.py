"""Testing the reformatting functions"""
import pytest
import auto_trader_client.src.validate_params as vp
from datetime import datetime

ORD_PARAMS = {
    "instruction": "BTO",
    "ticker": "INTC",
    "strike_price": "50.5",
    "contract_type": "C",
    "expiration": "12/31",
    "contract_price": "0.45",
    "comments": None,
}


def test_expiration_to_datetime():
    yr = datetime.today().year
    assert vp.expiration_str_to_datetime("1/1") == datetime(yr, 1, 1)
    assert vp.expiration_str_to_datetime("01/01") == datetime(yr, 1, 1)
    assert vp.expiration_str_to_datetime("1/01/" + str(yr)) == datetime(yr, 1, 1)
    assert vp.expiration_str_to_datetime("1/01/" + str(yr - 2000)) == datetime(yr, 1, 1)
    assert vp.expiration_str_to_datetime("12/31") == datetime(yr, 12, 31)
    assert vp.expiration_str_to_datetime("12/31/" + str(yr)) == datetime(yr, 12, 31)
    assert vp.expiration_str_to_datetime("12/31/" + str(yr - 2000)) == datetime(
        yr, 12, 31
    )


def test_reformat_params_good_input(monkeypatch):
    assert_dict = {
        "instruction": "BTO",
        "ticker": "INTC",
        "strike_price": "50.5",
        "contract_type": "C",
        "expiration": "12/31",
        "contract_price": "0.45",
        "comments": None,
    }
    yr = datetime.today().year

    def mock_expr_str_to_datetime(str):
        return datetime(yr, 12, 31)

    monkeypatch.setattr(vp, "expiration_str_to_datetime", mock_expr_str_to_datetime)
    monkeypatch.setitem(ORD_PARAMS, "expiration", datetime(yr, 12, 31))
    # test strike values that should be "50"
    monkeypatch.setitem(ORD_PARAMS, "strike_price", "50")
    strike_50 = ["50", "050", "50.", "50.0", "050.000"]
    for strike in strike_50:
        assert_dict["strike_price"] = strike
        assert vp.reformat_params(assert_dict) == ORD_PARAMS

    # test strike values that should be "50.5"
    monkeypatch.setitem(ORD_PARAMS, "strike_price", "50.5")
    strike_505 = ["50.5", "050.50", "50.500"]
    for strike in strike_505:
        assert_dict["strike_price"] = strike
        assert vp.reformat_params(assert_dict) == ORD_PARAMS

    # test strike values that should be "0.5"
    monkeypatch.setitem(ORD_PARAMS, "strike_price", "0.5")
    strike_point5 = ["0.5", "00.50", ".500", ".5"]
    for strike in strike_point5:
        assert_dict["strike_price"] = strike
        assert vp.reformat_params(assert_dict) == ORD_PARAMS


def test_reformat_params_raises_value_error(monkeypatch):
    illegal_vals = ["50.1", "50.01", "3.14"]
    for val in illegal_vals:
        monkeypatch.setitem(ORD_PARAMS, "strike_price", val)
        with pytest.raises(ValueError):
            vp.reformat_params(ORD_PARAMS)
