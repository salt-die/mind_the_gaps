import pytest

from mind_the_gaps import Endpoint


def test_endpoint_str():
    assert str(Endpoint(0, ")")) == "0)"
    assert str(Endpoint(0, "]")) == "0]"
    assert str(Endpoint(0, "(")) == "(0"
    assert str(Endpoint(0, "[")) == "[0"


def test_endpoint_properties():
    assert Endpoint(0, ")").is_open
    assert Endpoint(0, ")").is_right
    assert Endpoint(0, "(").is_open
    assert Endpoint(0, "(").is_left
    assert Endpoint(0, "[").is_closed
    assert Endpoint(0, "[").is_left
    assert Endpoint(0, "]").is_closed
    assert Endpoint(0, "]").is_right


def test_endpoint_lt_not_implemented():
    with pytest.raises(TypeError):
        Endpoint(0, "(") < 0
