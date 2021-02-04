import datetime
import auto_trader_client.src.validate_params as vp


ORD_PARAMS = {
    "instruction": "BTO",
    "ticker": "INTC",
    "strike_price": "50.5",
    "contract_type": "C",
    "expiration": "12/31",
    "contract_price": "0.45",
    "comments": None,
}


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
