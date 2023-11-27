from mind_the_gaps import Endpoint, Gaps


def test_left_open_not_contained():
    assert 0 not in Gaps([Endpoint(0, "("), 1])


def test_left_closed_contained():
    assert 0 in Gaps([0, 1])


def test_right_open_not_contained():
    assert 1 not in Gaps([0, Endpoint(1, ")")])


def test_right_closed_contained():
    assert 1 in Gaps([0, 1])
