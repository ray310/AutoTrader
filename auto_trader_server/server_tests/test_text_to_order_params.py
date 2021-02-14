""" Testing text_to_order_params.py function"""
import src.text_to_order_params as ttop

ORD_PARAMS = {
    "instruction": "BTO",
    "ticker": "INTC",
    "strike_price": "50",
    "contract_type": "C",
    "expiration": "12/31",
    "contract_price": "0.45",
    "comments": None,
    "flags": {"SL": None, "risk_level": None, "reduce": None},
}


def test_ttop_empty_string():
    """No input returns null order"""
    assert ttop.text_to_order_params("") is None


def test_ttop_no_signal():
    """String with no signal returns null order"""
    assert ttop.text_to_order_params("Closing 100% Positions") is None


def test_ttop_valid_signal():
    """Valid signal in string returns valid order parameters"""
    assert ttop.text_to_order_params("BTO INTC 50C 12/31 @0.45") == ORD_PARAMS


def test_ttop_signal_after_comment(monkeypatch):
    """Comments before signal are not captured"""
    assert ttop.text_to_order_params("comments BTO INTC 50C 12/31 @0.45") == ORD_PARAMS
    assert ttop.text_to_order_params("comments\nBTO INTC 50C 12/31 @0.45") == ORD_PARAMS


def test_ttop_embedded_signals(monkeypatch):
    """Only text after signal should be captured"""
    monkeypatch.setitem(ORD_PARAMS, "comments", " comments")
    assert (
        ttop.text_to_order_params("comments BTO INTC 50C 12/31 @0.45 comments")
        == ORD_PARAMS
    )
    monkeypatch.setitem(ORD_PARAMS, "comments", "\ncomments")
    assert (
        ttop.text_to_order_params("comments\nBTO INTC 50C 12/31 @0.45\ncomments")
        == ORD_PARAMS
    )


def test_ttop_only_parentheses_comment(monkeypatch):
    """Valid signal must either be followed by a space or open parentheses"""
    invalids = ["SL", "5", "[", "'", ",", ".", "!", "?", ")", "@", "%"]
    for invalid in invalids:
        assert ttop.text_to_order_params("BTO INTC 50C 12/31 @0.45" + invalid) is None

    temp_flag = {"SL": ".35", "risk_level": None, "reduce": None}
    monkeypatch.setitem(ORD_PARAMS, "flags", temp_flag)

    monkeypatch.setitem(ORD_PARAMS, "comments", "(SL @.35)")
    assert ttop.text_to_order_params("BTO INTC 50C 12/31 @0.45(SL @.35)") == ORD_PARAMS
    monkeypatch.setitem(ORD_PARAMS, "comments", " (SL @.35)")
    assert ttop.text_to_order_params("BTO INTC 50C 12/31 @0.45 (SL @.35)") == ORD_PARAMS


def test_ttop_two_valid_signals():
    """Two valid signals in same message return null"""
    string = "BTO INTC 50C 12/31 @0.45"
    assert ttop.text_to_order_params(string + " " + string) is None


def test_ttop_valid_instruction(monkeypatch):
    """Valid instruction BTO/STC returns valid order parameters"""
    valid_instructions = ["BTO", "STC"]
    for valid in valid_instructions:
        monkeypatch.setitem(ORD_PARAMS, "instruction", valid)
        assert ttop.text_to_order_params(valid + " INTC 50C 12/31 @0.45") == ORD_PARAMS


def test_ttop_invalid_instructions():
    """Otherwise valid signal with prefix that is
    not exactly capitalized 'BTO' or 'STC' returns null"""
    import itertools

    valid_instructions = ["BTO", "STC"]
    letters = []
    for instruction in valid_instructions:
        letters.extend(list(instruction.upper() + instruction.lower()))
    chars = set(letters)  # to remove duplicates
    cart_product = ["".join(x) for x in itertools.product(chars, repeat=3)]
    invalid_cart_product = [x for x in cart_product if x != "BTO" and x != "STC"]
    for combo in invalid_cart_product:
        assert ttop.text_to_order_params(combo + " INTC 50C 12/31 @.45") is None


def test_ttop_instruction_with_extra_char():
    """Extra characters before or after 'BTO' or 'STC' prefixes return null"""
    import itertools

    prefixes = ["BTO", "STC", "B", "C", "S", "T", "/"]
    extra_char_prefix = ["".join(x) for x in itertools.permutations(prefixes, 2)]
    for combo in extra_char_prefix:
        assert ttop.text_to_order_params(combo + " INTC 50C 12/31 @.45") is None


def test_ttop_valid_tickers(monkeypatch):
    """Tickers with 1-5 capital letters return valid order parameters"""
    tickers = [
        "I",
        "IN",
        "INT",
        "INTC",
        "INTCX",
    ]
    for ticker in tickers:
        monkeypatch.setitem(ORD_PARAMS, "ticker", ticker)
        assert (
            ttop.text_to_order_params("BTO " + ticker + " 50C 12/31 @0.45")
            == ORD_PARAMS
        )


def test_ttop_BTO_STC_ticker(monkeypatch):
    """BTO and STC tickers return valid order parameters"""
    instructions = ["BTO", "STC"]
    tickers = ["BTO", "STC"]
    for instruction in instructions:
        monkeypatch.setitem(ORD_PARAMS, "instruction", instruction)
        for ticker in tickers:
            monkeypatch.setitem(ORD_PARAMS, "ticker", ticker)
            assert (
                ttop.text_to_order_params(
                    instruction + " " + ticker + " 50C 12/31 @0.45"
                )
                == ORD_PARAMS
            )


def test_ttop_invalid_tickers():
    """Tickers not containing 1-5 capital letters return null"""
    tickers = [
        "",
        "5",
        "&",
        "f",
        "INTCXX",
        "intc",
        "INTC%",
        "IN^C",
        "5INTC",
        "INtC",
    ]
    for ticker in tickers:
        assert ttop.text_to_order_params("BTO " + ticker + " 50C 12/31 @0.45") is None


def test_ttop_valid_strike_price(monkeypatch):
    """Valid strike prices of 1-5 digits
    possibly followed by 1-2 decimals return valid order parameters"""
    strike_prices = [
        "1",
        "12",
        "123",
        "1234",
        "1234.5",
        "1234.56",
        "12345.5",
        "12345.67",
    ]
    for price in strike_prices:
        monkeypatch.setitem(ORD_PARAMS, "strike_price", price)
        assert (
            ttop.text_to_order_params("BTO INTC " + price + "C " "12/31 @0.45")
            == ORD_PARAMS
        )


def test_ttop_invalid_strike_price():
    """Invalid strike prices without 1-5 digits
    possibly followed by 1-2 decimals return null order"""
    strike_prices = [
        "",
        "122345",
        "1.121",
        "A",
        "B.12",
        "1234.C6",
        "12C",
        "12 ",
        "123.@",
    ]
    for price in strike_prices:
        assert (
            ttop.text_to_order_params("BTO INTC " + price + "C " "12/31 @0.45") is None
        )


def test_ttop_valid_contract_type(monkeypatch):
    """Valid contract type (C or P) returns valid order parameters"""
    valid_contract_types = ["C", "P"]
    for contract in valid_contract_types:
        monkeypatch.setitem(ORD_PARAMS, "contract_type", contract)
        assert (
            ttop.text_to_order_params("BTO INTC 50" + contract + " 12/31 @0.45")
            == ORD_PARAMS
        )


def test_ttop_invalid_contract_type():
    """Non-(C or P) contract types return null"""
    invalid_contract_types = [
        "",
        "c",
        "p",
        "S",
        "1",
        ".50",
        ".5",
        "@1.45",
        "INTC",
        "\\",
    ]
    for contract in invalid_contract_types:
        assert (
            ttop.text_to_order_params("BTO INTC 50" + contract + " 12/31 @0.45") is None
        )


def test_ttop_valid_expiration(monkeypatch):
    """# Valid expiration of 1-2 digits/ 1-2 digits
    then optionally /2 or 4 digit returns valid order parameters"""
    valid_expirations = ["1/2", "1/12", "12/1", "12/12"]
    valid_years = ["", "/34", "/3456"]
    for expiration in valid_expirations:
        for year in valid_years:
            monkeypatch.setitem(ORD_PARAMS, "expiration", expiration + year)
            assert (
                ttop.text_to_order_params(
                    "BTO INTC 50C " + expiration + year + " @0.45"
                )
                == ORD_PARAMS
            )


def test_ttop_invalid_expiration():
    """# Invalid expiration, not containing  1-2 digits/1-2 digits
    then optionally /2 or 4 digits returns null"""
    invalid_expiration = [
        "",
        "/",
        "/1",
        "1/",
        "12/",
        "/12",
        "123/1",
        "1/123",
        "12/123",
        "123/12",
        "123/123",
        "12/1234",
        "1234/12",
        "C/1",
        "1/C",
        "1//1",
    ]
    invalid_years = [
        "/",
        "/1",
        "123",
        "/123",
        "12345",
        "/12345",
        "/AB",
        "/1A",
        "/1234A",
        "/12",
    ]
    for expiration in invalid_expiration:
        for year in invalid_years:
            assert (
                ttop.text_to_order_params(
                    "BTO INTC 50C " + expiration + year + " @0.45"
                )
                is None
            )


def test_ttop_correct_at_syntax():
    """Contract price should come after @ with 0-1 spaces"""
    valid_at = ["@0.45", "@ 0.45"]
    for valid in valid_at:
        assert ttop.text_to_order_params("BTO INTC 50C 12/31 " + valid) == ORD_PARAMS


def test_ttop_wrong_at_syntax():
    """Missing @, or @ followed by characters other than 0-1 spaces,
    single '.' and valid price returns null"""
    invalid_at = [
        " 0.45",
        "0.45",
        "@test1.45",
        "@..45",
        "@ test1.45",
        "@ .1.45",
        "@1.a45",
        "@  0.45",
    ]
    for invalid in invalid_at:
        assert ttop.text_to_order_params("BTO INTC 50C 12/31 " + invalid) is None


def test_ttop_valid_contract_price(monkeypatch):
    """Valid contract prices of 0-3 digits followed
    by one or two decimals return valid order parameters"""
    valid_contract_prices = [
        ".12",
        "0.12",
        "12.34",
        "123.45",
        ".1",
        "0.1",
        "12.3",
        "123.4",
    ]
    for price in valid_contract_prices:
        monkeypatch.setitem(ORD_PARAMS, "contract_price", price)
        assert ttop.text_to_order_params("BTO INTC 50C 12/31 @" + price) == ORD_PARAMS


def test_ttop_invalid_contract_price():
    """Invalid contract prices not containing 0-4 digits followed
    by one or two decimals return null"""
    invalid_contract_prices = [
        "",
        "@",
        "/",
        "A",
        ".133",
        "z.1",
        "@2.z",
        "@1.23",
        "12.234",
        "1234.12",
        "12345.12",
        "12.12A",
        "1A.12",
    ]
    for price in invalid_contract_prices:
        assert ttop.text_to_order_params("BTO INTC 50C 12/31 @" + price) is None


def test_ttop_bto_sl(monkeypatch):
    """SL price is parsed from BTO order"""
    temp_flag = {"SL": ".35", "risk_level": None, "reduce": None}
    monkeypatch.setitem(ORD_PARAMS, "flags", temp_flag)
    monkeypatch.setitem(ORD_PARAMS, "comments", " (SL @.35)")
    assert ttop.text_to_order_params("BTO INTC 50C 12/31 @0.45 (SL @.35)") == ORD_PARAMS


def test_ttop_stc(monkeypatch):
    """SL price is not parsed from a STC order"""
    temp_flag = {"SL": None, "risk_level": None, "reduce": None}  # 'SL' is None
    monkeypatch.setitem(ORD_PARAMS, "flags", temp_flag)
    monkeypatch.setitem(ORD_PARAMS, "comments", " (SL @.35)")
    monkeypatch.setitem(ORD_PARAMS, "instruction", "STC")
    assert ttop.text_to_order_params("STC INTC 50C 12/31 @0.45 (SL @.35)") == ORD_PARAMS


def test_parse_sl_valid(monkeypatch):
    """SL price is returned from comments string"""
    monkeypatch.setitem(ORD_PARAMS, "instruction", "BTO")
    bases = ["SL@", "SL@ ", "SL @", "SL @ "]
    prices = ["1.45", "1.4", ".4", ".45"]
    for base in bases:
        for price in prices:
            comment = base + price

            monkeypatch.setitem(ORD_PARAMS, "comments", comment)
            assert ttop.parse_sl(ORD_PARAMS["comments"]) == price

            comment2 = "comments " + comment + " comments"
            monkeypatch.setitem(ORD_PARAMS, "comments", comment2)
            assert ttop.parse_sl(ORD_PARAMS["comments"]) == price


def test_parse_sl_invalid(monkeypatch):
    """Text with no valid SL instruction returns None"""
    monkeypatch.setitem(ORD_PARAMS, "instruction", "BTO")
    invalid_bases = ["SL", "@ ", "L@", "L @", "S@", "S @", ""]
    prices = ["1.45", "1.4", ".4", ".45"]
    for base in invalid_bases:
        for price in prices:
            comment = base + price

            monkeypatch.setitem(ORD_PARAMS, "comments", comment)
            assert ttop.parse_sl(ORD_PARAMS["comments"]) is None

    bases = ["SL@", "SL@ ", "SL @", "SL @ "]
    invalid_prices = ["1.453", "1234.4", "@ .4", "a.45", "1.45a", ""]
    for base in bases:
        for price in invalid_prices:
            comment = base + price

            monkeypatch.setitem(ORD_PARAMS, "comments", comment)
            assert ttop.parse_sl(ORD_PARAMS["comments"]) is None


def test_strip_markdown():
    """Should remove underscores and asterisks"""
    test_str = "***___***te*_st***___***"
    assert ttop.strip_markdown(test_str) == "test"