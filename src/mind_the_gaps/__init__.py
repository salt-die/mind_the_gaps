"""A library for unions, intersections, subtractions, and xors of intervals (gaps)."""
from .gaps import Endpoint, Gaps, GapsNotSorted, NegativeInfinity, PositiveInfinity
from .var import x

__all__ = [
    "Endpoint",
    "Gaps",
    "GapsNotSorted",
    "NegativeInfinity",
    "PositiveInfinity",
    "x",
]

__version__ = "0.2.0"
