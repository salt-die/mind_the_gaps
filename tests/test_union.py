from mind_the_gaps import Endpoint, Gaps


def test_bounded_disjoint_a_and_b():
    a = Gaps([Endpoint(0, "["), Endpoint(1, "]")])
    b = Gaps([Endpoint(2, "["), Endpoint(3, "]")])

    assert a | b == Gaps(
        [Endpoint(0, "["), Endpoint(1, "]"), Endpoint(2, "["), Endpoint(3, "]")]
    )
