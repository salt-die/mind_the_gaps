from mind_the_gaps import Gaps


def test_bounded_disjoint():
    a = Gaps([0, 1])
    b = Gaps([2, 3])
    assert a & b == Gaps()


def test_unbounded_disjoint():
    a = Gaps([-float("inf"), 0])
    b = Gaps([1, 2])
    assert a & b == Gaps()


def test_bounded_intersecting_proper():
    a = Gaps([0, 2])
    b = Gaps([1, 3])
    assert a & b == Gaps([1, 2])


def test_bounded_intersecting_singleton():
    a = Gaps([0, 2])
    b = Gaps([1, 1])
    assert a & b == b


def test_empty_intersection():
    a = Gaps([0, 2])
    b = Gaps()
    assert a & b == b