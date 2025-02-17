from __future__ import annotations

from bisect import bisect
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import total_ordering
from itertools import pairwise
from operator import and_, attrgetter, or_, xor
from typing import Any, Final, Literal, Protocol, Self

__all__ = ["Endpoint", "Gaps"]

Boundary = Literal["(", ")", "[", "]"]
"""The boundary of an endpoint.

`"("` is open and left, `")"` is open and right,`"["` is closed and left, and
`"]"` is closed and right.
"""

_BOUNDARY_ORDER: Final[dict[Boundary, int]] = {")": 0, "[": 1, "]": 1, "(": 2}


def sub(a: bool, b: bool) -> bool:
    """`a` and not `b`."""
    return a and not b


class SupportsLessThan(Protocol):
    """Supports the less-than (`<`) operator."""

    def __lt__(self, other: Any, /) -> bool: ...


@total_ordering
@dataclass(frozen=True, slots=True)
class Endpoint[T: SupportsLessThan]:
    """An interval endpoint."""

    value: T
    """Value of endpoint."""
    boundary: Boundary
    """The boundary of an endpoint.

    `"("` is open and left, `")"` is open and right,`"["` is closed and left, and
    `"]"` is closed and right.
    """

    def __lt__(self, other: Endpoint) -> bool:
        if not isinstance(other, Endpoint):
            return NotImplemented

        if self.value != other.value:
            return self.value < other.value

        return _BOUNDARY_ORDER[self.boundary] < _BOUNDARY_ORDER[other.boundary]

    def __eq__(self, other: Endpoint) -> bool:
        if not isinstance(other, Endpoint):
            return NotImplemented

        return (
            self.value == other.value
            and _BOUNDARY_ORDER[self.boundary] == _BOUNDARY_ORDER[other.boundary]
        )

    def __str__(self):
        if self.is_left:
            return f"{self.boundary}{self.value}"
        return f"{self.value}{self.boundary}"

    @property
    def is_closed(self) -> bool:
        """Whether this is a closed endpoint."""
        return self.boundary in "[]"

    @property
    def is_open(self) -> bool:
        """Whether this is an open endpoint."""
        return self.boundary in "()"

    @property
    def is_left(self) -> bool:
        """Whether this is a left endpoint."""
        return self.boundary in "[("

    @property
    def is_right(self) -> bool:
        """Whether this is a right endpoint."""
        return self.boundary in ")]"


def _endpoint_contains[T](endpoint: Endpoint[T] | None, value: T) -> bool:
    """Return whether value could be contained in an interval with given endpoint."""
    if endpoint is None:
        return False
    if endpoint.value == value:
        return endpoint.is_closed
    if endpoint.is_left:
        return value > endpoint.value
    return value < endpoint.value


def _endpoint_contains_right[T](endpoint: Endpoint[T] | None, value: T) -> bool:
    """Return whether value with a positive offset could be contained in an interval
    with given endpoint.
    """
    if endpoint is None:
        return False
    if endpoint.is_left:
        return value >= endpoint.value
    return value < endpoint.value


def _merge[T](
    a: list[Endpoint[T]], b: list[Endpoint[T]], op: Callable[[bool, bool], bool]
) -> list[Endpoint[T]]:
    """Merge two sorted lists of endpoints with a given set operation."""
    endpoints: list[Endpoint[T]] = []
    i: int = 0
    j: int = 0
    inside_region: bool = False
    scanline: T
    current_a: Endpoint[T] | None = None
    current_b: Endpoint[T] | None = None

    while i < len(a) or j < len(b):
        if i >= len(a):
            current_b = b[j]
            scanline = current_b.value
            j += 1
        elif j >= len(b):
            current_a = a[i]
            scanline = current_a.value
            i += 1
        else:
            current_a = a[i]
            current_b = b[j]
            scanline = min(current_a.value, current_b.value)
            i += current_a.value == scanline
            j += current_b.value == scanline

        at_scanline = op(
            _endpoint_contains(current_a, scanline),
            _endpoint_contains(current_b, scanline),
        )  # Whether scanline is contained in region.

        right_of_scanline = op(
            _endpoint_contains_right(current_a, scanline),
            _endpoint_contains_right(current_b, scanline),
        )  # Whether scanline with a positive offset is contained in region.

        if inside_region:
            if not right_of_scanline:
                endpoints.append(Endpoint(scanline, "]" if at_scanline else ")"))
                inside_region = False
            elif not at_scanline:
                endpoints.append(Endpoint(scanline, ")"))
                endpoints.append(Endpoint(scanline, "("))
        else:
            if right_of_scanline:
                endpoints.append(Endpoint(scanline, "[" if at_scanline else "("))
                inside_region = True
            elif at_scanline:
                endpoints.append(Endpoint(scanline, "["))
                endpoints.append(Endpoint(scanline, "]"))

    return endpoints


def _to_number(text: str) -> int | float:
    try:
        return int(text)
    except ValueError:
        return float(text)


@dataclass
class Gaps[T: SupportsLessThan]:
    """A set of mutually exclusive continuous intervals.

    `Gaps` are created with an ordered sequence of endpoints or values with alternating
    endpoints representing the left or right endpoint of an interval. Endpoints that are
    just values and not of type `Endpoint` will be converted to an `Endpoint` with a closed
    boundary so that ::

        Gaps([1, 2]) == Gaps([Endpoint(1, "["), Endpoint(2, "]")])

    is true.
    """

    endpoints: list[T | Endpoint[T]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.endpoints) % 2 == 1:
            raise ValueError("Need an even number of endpoints.")

        for i, endpoint in enumerate(self.endpoints):
            if not isinstance(endpoint, Endpoint):
                self.endpoints[i] = Endpoint(endpoint, "[" if i % 2 == 0 else "]")
            elif i % 2 == 0 and endpoint.is_right:
                raise ValueError(f"Expected left boundary, got {endpoint!r}.")
            elif i % 2 == 1 and endpoint.is_left:
                raise ValueError(f"Expected right boundary, got {endpoint!r}.")

        i = 0
        while i < len(self.endpoints) - 1:
            a = self.endpoints[i]
            b = self.endpoints[i + 1]
            if a > b:
                raise ValueError(f"Endpoints unsorted. {a!r} > {b!r}")
            if a.value == b.value and a.boundary + b.boundary not in {"[]", ")("}:
                # Intervals aren't minimally expressed, but can be fixed by removing
                # these endpoints.
                del self.endpoints[i : i + 2]
            else:
                i += 1

    @classmethod
    def from_string(cls, gaps: str) -> Self[int | float]:
        """Create gaps from a string.

        Values can only be int or float. Uses standard interval notation, i.e.,
        `"{(-inf, 1], [2, 3)}"`. If the start and end value of an interval are equal,
        the interval may be expressed as, e.g., `"{[0]}"`.
        """
        if gaps[0] != "{" or gaps[-1] != "}":
            raise ValueError(
                "Gap string must start and end with curly braces ('{', '}')."
            )

        splits = gaps[1:-1].replace(" ", "").split(",")
        if len(splits) == 1 and splits[0] == "":
            return cls([])

        endpoints: list[Endpoint[int | float]] = []
        for split in splits:
            if split.startswith("[") and split.endswith("]"):
                value = _to_number(split[1:-1])
                endpoints.append(Endpoint(value, "["))
                endpoints.append(Endpoint(value, "]"))
            elif split.startswith(("(", "[")):
                value = _to_number(split[1:])
                endpoints.append(Endpoint(value, split[0]))
            elif split.endswith((")", "]")):
                value = _to_number(split[:-1])
                endpoints.append(Endpoint(value, split[-1]))
            else:
                raise ValueError(f"Invalid endpoint ({split!r}).")

        return cls(endpoints)

    def __or__(self, other: Gaps) -> Self:
        if not isinstance(other, Gaps):
            return NotImplemented

        return type(self)(_merge(self.endpoints, other.endpoints, or_))

    def __and__(self, other: Gaps) -> Self:
        if not isinstance(other, Gaps):
            return NotImplemented

        return type(self)(_merge(self.endpoints, other.endpoints, and_))

    def __xor__(self, other: Gaps) -> Self:
        if not isinstance(other, Gaps):
            return NotImplemented

        return type(self)(_merge(self.endpoints, other.endpoints, xor))

    def __sub__(self, other: Gaps) -> Self:
        if not isinstance(other, Gaps):
            return NotImplemented

        return type(self)(_merge(self.endpoints, other.endpoints, sub))

    def __bool__(self) -> bool:
        return len(self.endpoints) > 0

    def __contains__(self, value: T) -> bool:
        i = bisect(self.endpoints, value, key=attrgetter("value"))
        if i == 0:
            return False

        if self.endpoints[i - 1].value == value:
            return self.endpoints[i - 1].is_closed

        if i < len(self.endpoints):
            return self.endpoints[i].is_right

        return False

    def __str__(self) -> str:
        endpoints = []
        for a, b in pairwise(self.endpoints):
            if a == b:
                endpoints.append(f"[{a.value}]")
            else:
                endpoints.append(str(a))
        if a != b:
            endpoints.append(str(b))
        return f"{{{", ".join(endpoints)}}}"
