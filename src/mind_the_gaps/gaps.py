from bisect import bisect
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import total_ordering
from operator import and_, attrgetter, or_, xor
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
@dataclass(frozen=True, slots=True)
class Endpoint[T: SupportsLessThan]:
    """An interval endpoint."""

    value: T
    """Value of endpoint."""
    boundary: Literal["(", ")", "[", "]"]
    """
    The type of boundary.

    `"("` is open and left, `")"` is open and right,`"["` is closed and left, and
    `"]"` is closed and right.
    """

    def __lt__(self, other: Self) -> bool:
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
    """
    Merge two sorted lists of endpoints with a given set operation.

    This is a sweep-line algorithm; as each endpoint is encounted one of
    `inside_a` or `inside_b` is flipped depending on whether the point belongs
    to `a` or `b`. This may flip `inside_region` (depending on `op`) which adds
    a new endpoint to the output.
    """
    endpoints: list[Endpoint] = []
    i: int = 0
    j: int = 0
    inside_a: bool = False
    inside_b: bool = False
    inside_region: bool = False

    MAX_ENDPOINT = Endpoint(PositiveInfinity(), "(")
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


@dataclass
class Gaps[T: SupportsLessThan]:
    """
    A set of mutually exclusive continuous intervals.

    `Gaps` are created with an ordered sequence of endpoints or values with alternating
    endpoints representing the left or right endpoint of an interval. Endpoints that are
    just values and not of type `Endpoint` will be converted to an `Endpoint` with a closed
    boundary so that ::

        Gaps([1, 2]) == Gaps([Endpoint(1, "["), Endpoint(2, "]")])

    is true.
    """

    endpoints: list[T | Endpoint[T]] = field(default_factory=list)

    def __post_init__(self):
        if len(self.endpoints) % 2 == 1:
            raise ValueError("Need an even number of endpoints.")

        for i, endpoint in enumerate(self.endpoints):
            if not isinstance(endpoint, Endpoint):
                self.endpoints[i] = Endpoint(endpoint, "[" if i % 2 == 0 else "]")
            elif i % 2 == 0 and endpoint.boundary in ")]":
                raise ValueError(f"Expected left boundary, got {endpoint!r}.")
            elif i % 2 == 1 and endpoint.boundary in "([":
                raise ValueError(f"Expected right boundary, got {endpoint!r}.")

        for i in range(len(self.endpoints) - 1):
            a = self.endpoints[i]
            b = self.endpoints[i + 1]
            if a.value > b.value:
                raise ValueError("Intervals unsorted.")
            if a.value == b.value and a.boundary + b.boundary in {"](", ")["}:
                raise ValueError(
                    f"Intervals not minimally expressed. Endpoints {a!r} and {b!r} can be removed."
                )

    @classmethod
    def from_string(cls, gaps: str) -> Self:
        """
        Create gaps from a string.

        Values can only be int or float. Uses standard interval notation, i.e., `"{(-inf, 1], [2, 3)}"`.
        """
        if gaps[0] != "{" or gaps[-1] != "}":
            raise ValueError(
                "Gap string must start and end with curly braces ('{', '}')."
            )

        endpoints = gaps[1:-1].replace(" ", "").split(",")
        if len(endpoints) == 1:
            return cls([])

        for i, endpoint in enumerate(endpoints):
            if endpoint.startswith(("(", "[")):
                boundary = endpoint[0]
                value = endpoint[1:]
            elif endpoint.endswith((")", "]")):
                boundary = endpoint[-1]
                value = endpoint[:-1]
            else:
                raise ValueError(f"Invalid endpoint ({endpoint!r}).")

            try:
                value = int(value)
            except ValueError:
                value = float(value)

            endpoints[i] = Endpoint(value, boundary)

        return cls(endpoints)

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

    def __contains__(self, value: T) -> bool:
        i = bisect(self.endpoints, value, key=attrgetter("value"))
        if i == 0:
            return False

        if self.endpoints[i - 1].value == value:
            return self.endpoints[i - 1].boundary in "[]"

        return self.endpoints[i].boundary in "])"

    def __str__(self):
        return f"{{{", ".join(str(endpoint) for endpoint in self.endpoints)}}}"
