import pytest

from mind_the_gaps import Endpoint, Gaps


def test_singleton_ok():
    Gaps([1, 1])


def test_missing_singleton_ok():
    Gaps([0, Endpoint(1, ")"), Endpoint(1, "("), 2])


def test_fix_not_minimally_expressed():
    assert Gaps([0, Endpoint(1, ")"), 1, 2]) == Gaps([0, 2])
    assert Gaps([0, 1, Endpoint(1, "("), 2]) == Gaps([0, 2])
    assert Gaps([0, 0, 0, 0]) == Gaps([0, 0])
    assert Gaps([1, 2, 2, 3]) == Gaps([1, 3])


def test_unsorted_closed():
    with pytest.raises(ValueError, match="unsorted"):
        Gaps([1, 0])


def test_unsorted_open():
    with pytest.raises(ValueError, match="unsorted"):
        Gaps([Endpoint(1, "("), Endpoint(0, ")")])


def test_unsorted_open_closed():
    with pytest.raises(ValueError, match="unsorted"):
        Gaps([Endpoint(0, "("), 0, 1, 2])


def test_unsorted_closed_open():
    with pytest.raises(ValueError, match="unsorted"):
        Gaps([0, Endpoint(0, ")"), 1, 2])


def test_unsorted_open_open():
    with pytest.raises(ValueError, match="unsorted"):
        Gaps([Endpoint(1, "("), Endpoint(1, ")")])


def test_wrong_boundary():
    with pytest.raises(ValueError, match="left"):
        Gaps([Endpoint(0, "]"), 1])

    with pytest.raises(ValueError, match="left"):
        Gaps([Endpoint(0, ")"), 1])

    with pytest.raises(ValueError, match="right"):
        Gaps([0, Endpoint(1, "[")])

    with pytest.raises(ValueError, match="right"):
        Gaps([0, Endpoint(1, "(")])


def test_wrong_number_of_endpoints():
    with pytest.raises(ValueError, match="endpoints"):
        Gaps([0, 1, 2])


def test_gap_bool():
    assert bool(Gaps([0, 1]))
    assert not bool(Gaps())


def test_gap_str():
    assert str(Gaps([0, 1])) == "{[0, 1]}"
    assert str(Gaps([Endpoint(0, "("), 1])) == "{(0, 1]}"
    assert str(Gaps([0, Endpoint(1, ")")])) == "{[0, 1)}"
    assert str(Gaps([Endpoint(0, "("), Endpoint(1, ")")])) == "{(0, 1)}"
    assert str(Gaps([0, 0])) == "{[0]}"


def test_gap_not_implemented():
    with pytest.raises(TypeError):
        Gaps() | None

    with pytest.raises(TypeError):
        Gaps() - None

    with pytest.raises(TypeError):
        Gaps() & None

    with pytest.raises(TypeError):
        Gaps() ^ None
