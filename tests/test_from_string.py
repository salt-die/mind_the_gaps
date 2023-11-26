from mind_the_gaps import Endpoint, Gaps


def test_from_string_closed():
    assert Gaps.from_string("{[0, 1], [2, 3]}") == Gaps([0, 1, 2, 3])


def test_from_string_open():
    assert Gaps.from_string("{(0, 1), (2, 3)}") == Gaps(
        [Endpoint(0, "("), Endpoint(1, ")"), Endpoint(2, "("), Endpoint(3, ")")]
    )


def test_from_string_half_open():
    assert Gaps.from_string("{(-inf, 0], [1, 2)}") == Gaps(
        [Endpoint(-float("inf"), "("), 0, 1, Endpoint(2, ")")]
    )


def test_from_string_singleton():
    assert Gaps.from_string("{[0, 0]}") == Gaps([0, 0])


def test_from_string_empty():
    assert Gaps.from_string("{}") == Gaps()
