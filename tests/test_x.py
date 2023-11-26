from mind_the_gaps import Endpoint, Gaps, x


def test_x_closed():
    assert Gaps([0 <= x, x <= 1, 2 <= x, x <= 3]) == Gaps([0, 1, 2, 3])


def test_x_open():
    assert Gaps([0 < x, x < 1, 2 < x, x < 3]) == Gaps(
        [Endpoint(0, "("), Endpoint(1, ")"), Endpoint(2, "("), Endpoint(3, ")")]
    )


def test_x_singleton():
    assert Gaps([0 <= x, x <= 0]) == Gaps([0, 0])
