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


def test_valid_params():
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
