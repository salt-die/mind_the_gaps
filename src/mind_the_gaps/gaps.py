from collections.abc import Callable
from dataclasses import dataclass, field
from functools import total_ordering
from operator import and_, or_, xor
from typing import Literal, Protocol, Self

__all__ = ["PositiveInfinity", "NegativeInfinity", "Endpoint", "Gaps"]


def sub(a: bool, b: bool) -> bool:
    """`a` and not `b`."""
    return a and not b


class SupportsLessThan(Protocol):
    """Supports the less-than (`<`) operator."""

    def __lt__(self, other) -> bool:
        ...


class PositiveInfinity(SupportsLessThan):
    """
    Positive infinity for non-numeric types.

    Positive infinity is greater-than all other values.
    """

    def __eq__(self, other: SupportsLessThan) -> bool:
        return isinstance(other, PositiveInfinity)

    def __lt__(self, _: SupportsLessThan) -> Literal[False]:
        return False

    def __le__(self, other: SupportsLessThan) -> bool:
        return isinstance(other, PositiveInfinity)

    def __gt__(self, other: SupportsLessThan) -> bool:
        return not isinstance(other, PositiveInfinity)

    def __ge__(self, _: SupportsLessThan) -> Literal[True]:
        return True

    def __repr__(self):
        return "PositiveInfinity()"

    def __str__(self):
        return "∞"


class NegativeInfinity(SupportsLessThan):
    """
    Negative infinity for non-numeric types.

    Negative infinity is less-than all other values.
    """

    def __eq__(self, other: SupportsLessThan) -> bool:
        return isinstance(other, NegativeInfinity)

    def __lt__(self, other: SupportsLessThan) -> bool:
        return not isinstance(other, NegativeInfinity)

    def __le__(self, _: SupportsLessThan) -> Literal[True]:
        return True

    def __gt__(self, _: SupportsLessThan) -> Literal[False]:
        return False

    def __ge__(self, other: SupportsLessThan) -> bool:
        return isinstance(other, NegativeInfinity)

    def __repr__(self):
        return "NegativeInfinity()"

    def __str__(self):
        return "-∞"


@total_ordering
@dataclass
class Endpoint[SupportsLessThan]:
    """An interval endpoint."""

    value: SupportsLessThan
    """Value of endpoint."""
    boundary: Literal["(", ")", "[", "]"]
    """
    The type of boundary.

    A boundary can be either open or closed and either left or right "(" is open
    and left, ")" is open and right,"[" is closed and left, and "]" is closed and right.
    """

    def __lt__(self, other: "Endpoint") -> bool:
        if self.value != other.value:
            return self.value < other.value

        return self.boundary + other.boundary in {"[(", ")]", "][", "](", ")[", ")("}

    def __str__(self):
        if self.boundary in "([":
            return f"{self.boundary}{self.value}"
        return f"{self.value}{self.boundary}"


def _merge(
    a: list[Endpoint], b: list[Endpoint], op: Callable[[bool, bool], bool]
) -> list[Endpoint]:
    """Merge two sorted lists of endpoints with a given set operation."""
    endpoints: list[Endpoint] = []
    i: int = 0
    j: int = 0
    inside_a: bool = False
    inside_b: bool = False
    inside_region: bool = False

    MAX_ENDPOINT = Endpoint(PositiveInfinity(), "[")
    while i < len(a) or j < len(b):
        current_a = a[i] if i < len(a) else MAX_ENDPOINT
        current_b = b[j] if j < len(b) else MAX_ENDPOINT
        current_endpoint = min(current_a, current_b)

        if current_a == current_endpoint:
            inside_a = not inside_a
            i += 1

        if current_b == current_endpoint:
            inside_b = not inside_b
            j += 1

        if op(inside_a, inside_b) != inside_region:
            inside_region = not inside_region

            closed = current_endpoint.boundary in "[]"
            b_in_a = inside_a and current_b == current_endpoint
            a_in_b = inside_b and current_a == current_endpoint
            if op == sub and b_in_a or op == xor and (a_in_b or b_in_a):
                closed = not closed
            boundary = (")(", "][")[closed][len(endpoints) % 2 == 0]
            if (
                len(endpoints) > 0
                and endpoints[-1].value == current_endpoint.value
                and endpoints[-1].boundary + boundary not in {"[]", ")("}
            ):
                endpoints.pop()
            else:
                endpoints.append(Endpoint(current_endpoint.value, boundary))

    return endpoints


class GapsNotSorted(Exception):
    ...


@dataclass
class Gaps[SupportsLessThan]:
    """
    A set of mutually exclusive continuous intervals.

    Gaps can be created from list of endpoints or from a list of values that support less-than.
    If created from a list of values, they'll be converted to endpoints with closed boundaries.
    """

    endpoints: list[SupportsLessThan | Endpoint[SupportsLessThan]] = field(
        default_factory=list
    )

    def __post_init__(self):
        for i, endpoint in enumerate(self.endpoints):
            if not isinstance(endpoint, Endpoint):
                self.endpoints[i] = Endpoint(endpoint, "[" if i % 2 == 0 else "]")

        for i in range(len(self.endpoints) - 1):
            a = self.endpoints[i]
            b = self.endpoints[i + 1]
            if a.value > b.value or (
                a.value == b.value and a.boundary + b.boundary not in {"[]", ")("}
            ):
                raise GapsNotSorted("Intervals overlap or are unsorted.")

    def __invert__(self) -> Self:
        return self ^ Gaps(
            [Endpoint(NegativeInfinity(), "("), Endpoint(PositiveInfinity(), ")")]
        )

    def __or__(self, other: Self) -> Self:
        return Gaps(_merge(self.endpoints, other.endpoints, or_))

    def __and__(self, other: Self) -> Self:
        return Gaps(_merge(self.endpoints, other.endpoints, and_))

    def __xor__(self, other: Self) -> Self:
        return Gaps(_merge(self.endpoints, other.endpoints, xor))

    def __sub__(self, other: Self) -> Self:
        return Gaps(_merge(self.endpoints, other.endpoints, sub))

    def __str__(self):
        return f"{{{", ".join(str(endpoint) for endpoint in self.endpoints)}}}"
