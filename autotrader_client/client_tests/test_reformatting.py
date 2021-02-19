"""Testing the reformatting functions"""
import pytest
import itertools
import src.validate_params as vp
from datetime import datetime


OUTPUT_PARAMS = {
    "instruction": "BTO",
    "ticker": "INTC",
    "strike_price": "50.5",
    "contract_type": "C",
    "expiration": datetime(datetime.today().year, 12, 31),
    "contract_price": 0.45,
    "comments": None,
    "flags": {"SL": 0.31, "risk_level": None, "reduce": None},
}

INPUT = {
    "instruction": "BTO",
    "ticker": "INTC",
    "strike_price": "50.5",
    "contract_type": "C",
    "expiration": "12/31",
    "contract_price": "0.45",
    "comments": None,
    "flags": {"SL": ".31", "risk_level": None, "reduce": None},
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


def test_reformat_params_valid_prices(monkeypatch):
    """ Strike, contract, and stop-loss prices reformat correctly"""
    yr = datetime.today().year

    def mock_expr_str_to_datetime(string):
        return datetime(yr, 12, 31)

    monkeypatch.setattr(vp, "expiration_str_to_datetime", mock_expr_str_to_datetime)

    # create tuples where the first value should be reformatted to the second
    strike_50 = ["50", "050", "50.", "50.0", "050.000"]
    strike_505 = ["50.5", "050.50", "50.500"]
    strike_point5 = ["0.5", "00.50", ".500", ".5"]
    input_output_tuples = []
    input_output_tuples.extend(zip(strike_50, itertools.repeat("50")))
    input_output_tuples.extend(zip(strike_505, itertools.repeat("50.5")))
    input_output_tuples.extend(zip(strike_point5, itertools.repeat("0.5")))

    for tup in input_output_tuples:
        monkeypatch.setitem(INPUT, "strike_price", tup[0])
        monkeypatch.setitem(OUTPUT_PARAMS, "strike_price", tup[1])
        assert vp.reformat_params(INPUT) == OUTPUT_PARAMS


def test_reformat_params_raises_value_error(monkeypatch):
    illegal_vals = ["50.1", "50.01", "3.14"]
    for val in illegal_vals:
        monkeypatch.setitem(INPUT, "strike_price", val)
        with pytest.raises(ValueError):
            vp.reformat_params(INPUT)


def test_reformat_params_reduction(monkeypatch):
    """reformat_params should remove "%" and convert to float"""
    yr = datetime.today().year

    def mock_expr_str_to_datetime(string):
        return datetime(yr, 12, 31)

    monkeypatch.setattr(vp, "expiration_str_to_datetime", mock_expr_str_to_datetime)

    input_flags = {"SL": None, "risk_level": None, "reduce": "50%"}
    output_flags = {"SL": None, "risk_level": None, "reduce": 0.5}
    monkeypatch.setitem(INPUT, "flags", input_flags)
    monkeypatch.setitem(OUTPUT_PARAMS, "flags", output_flags)
    assert isinstance(INPUT["expiration"], str)
    assert vp.reformat_params(INPUT) == OUTPUT_PARAMS
