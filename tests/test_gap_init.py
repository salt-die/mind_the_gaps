import pytest
from mind_the_gaps import Endpoint, Gaps


def test_unsorted_closed():
    with pytest.raises(ValueError, match="unsorted"):
        Gaps([1, 0])


def test_unsorted_open():
    with pytest.raises(ValueError, match="unsorted"):
        Gaps([Endpoint(1, "("), Endpoint(0, ")")])


def test_singleton_ok():
    Gaps([1, 1])


def test_missing_singleton_ok():
    Gaps([0, Endpoint(1, ")"), Endpoint(1, "("), 2])


def test_open_closed():
    with pytest.raises(ValueError, match="not minimally expressed"):
        Gaps([0, Endpoint(1, ")"), 1, 2])


def test_closed_open():
    with pytest.raises(ValueError, match="not minimally expressed"):
        Gaps([0, 1, Endpoint(1, "("), 2])
