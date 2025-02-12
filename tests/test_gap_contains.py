from mind_the_gaps import Endpoint, Gaps


def test_left_open_not_contained():
    assert 0 not in Gaps([Endpoint(0, "("), 1])


def test_left_closed_contained():
    assert 0 in Gaps([0, 1])


def test_right_open_not_contained():
    assert 1 not in Gaps([0, Endpoint(1, ")")])


def test_right_closed_contained():
    assert 1 in Gaps([0, 1])


def test_value_less_than_first_endpoint_not_containted():
    assert -1 not in Gaps([0, 1])


def test_value_greater_than_last_endpoint_not_contained():
    assert 7 not in Gaps([0, 1])


def test_value_not_equal_to_endpoint_but_contained():
    assert 0.5 in Gaps([0, 1])


def test_value_not_equal_to_endpoint_but_not_contained():
    assert 1.5 not in Gaps([0, 1, 2, 3])
