from mind_the_gaps import Endpoint, Gaps


def test_bounded_disjoint():
    a = Gaps([0, 1])
    b = Gaps([2, 3])
    assert a | b == Gaps([0, 1, 2, 3])


def test_unbounded_disjoint():
    a = Gaps([-float("inf"), 0])
    b = Gaps([1, 2])
    assert a | b == Gaps([-float("inf"), 0, 1, 2])


def test_bounded_intersecting_proper():
    a = Gaps([0, 2])
    b = Gaps([1, 3])
    assert a | b == Gaps([0, 3])


def test_bounded_intersecting_singleton():
    a = Gaps([0, 2])
    b = Gaps([1, 1])
    assert a | b == a


def test_bounded_missing_singleton():
    a = Gaps([0, 2])
    b = Gaps([0, Endpoint(1, ")"), Endpoint(1, "("), 2])
    assert a | b == a


def test_empty_union():
    a = Gaps([0, 2])
    b = Gaps()
    assert a | b == a
