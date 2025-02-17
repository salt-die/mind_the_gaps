from mind_the_gaps import Gaps

LEFT_OPERANDS = [
    "{[0, 3), (5, 7]}",
    "{[1, 5), (6, 9]}",
    "{[0, 2), (4, 6]}",
    "{[0, 2], (4, 6)}",
    "{(1, 4], [5, 7)}",
    "{[0, 6]}",
    "{[0, 1], (3, 4], [6, 7)}",
    "{[0, 4), (6, 10]}",
    "{[1, 3), (5, 7]}",
    "{[0, 10]}",
]

RIGHT_OPERANDS = [
    "{(2, 4], (6, 8]}",
    "{[2, 4), (7, 8]}",
    "{(2, 3), (7, 9]}",
    "{(2, 4], (6, 8]}",
    "{[1, 4), (5, 7]}",
    "{(1, 2], (3, 5)}",
    "{(1, 2), [4, 5), (7, 8]}",
    "{(2, 5], (11, 13]}",
    "{[3, 5), (7, 9]}",
    "{(3, 4), (7, 8]}",
]

INTERSECTIONS = [
    "{(2, 3), (6, 7]}",
    "{[2, 4), (7, 8]}",
    "{}",
    "{}",
    "{(1, 4), (5, 7)}",
    "{(1, 2], (3, 5)}",
    "{[4]}",
    "{(2, 4)}",
    "{}",
    "{(3, 4), (7, 8]}",
]

SUBTRACTIONS = [
    "{[0, 2], (5, 6]}",
    "{[1, 2), [4, 5), (6, 7], (8, 9]}",
    "{[0, 2), (4, 6]}",
    "{[0, 2], (4, 6)}",
    "{[4], [5]}",
    "{[0, 1], (2, 3], [5, 6]}",
    "{[0, 1], (3, 4), [6, 7)}",
    "{[0, 2], (6, 10]}",
    "{[1, 3), (5, 7]}",
    "{[0, 3], [4, 7], (8, 10]}",
]

UNIONS = [
    "{[0, 4], (5, 8]}",
    "{[1, 5), (6, 9]}",
    "{[0, 2), (2, 3), (4, 6], (7, 9]}",
    "{[0, 6), (6, 8]}",
    "{[1, 4], [5, 7]}",
    "{[0, 6]}",
    "{[0, 2), (3, 5), [6, 7), (7, 8]}",
    "{[0, 5], (6, 10], (11, 13]}",
    "{[1, 5), (5, 9]}",
    "{[0, 10]}",
]

XORS = [
    "{[0, 2], [3, 4], (5, 6], (7, 8]}",
    "{[1, 2), [4, 5), (6, 7], (8, 9]}",
    "{[0, 2), (2, 3), (4, 6], (7, 9]}",
    "{[0, 6), (6, 8]}",
    "{[1], [4], [5], [7]}",
    "{[0, 1], (2, 3], [5, 6]}",
    "{[0, 2), (3, 4), (4, 5), [6, 7), (7, 8]}",
    "{[0, 2], [4, 5], (6, 10], (11, 13]}",
    "{[1, 5), (5, 9]}",
    "{[0, 3], [4, 7], (8, 10]}",
]


def test_intersections():
    for left, right, result in zip(LEFT_OPERANDS, RIGHT_OPERANDS, INTERSECTIONS):
        a = Gaps.from_string(left)
        b = Gaps.from_string(right)
        c = Gaps.from_string(result)
        assert a & b == c


def test_subtractions():
    for left, right, result in zip(LEFT_OPERANDS, RIGHT_OPERANDS, SUBTRACTIONS):
        a = Gaps.from_string(left)
        b = Gaps.from_string(right)
        c = Gaps.from_string(result)
        assert a - b == c


def test_unions():
    for left, right, result in zip(LEFT_OPERANDS, RIGHT_OPERANDS, UNIONS):
        a = Gaps.from_string(left)
        b = Gaps.from_string(right)
        c = Gaps.from_string(result)
        assert a | b == c


def test_xors():
    for left, right, result in zip(LEFT_OPERANDS, RIGHT_OPERANDS, XORS):
        a = Gaps.from_string(left)
        b = Gaps.from_string(right)
        c = Gaps.from_string(result)
        assert a ^ b == c
