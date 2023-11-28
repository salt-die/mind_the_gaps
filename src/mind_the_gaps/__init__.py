"""A library for unions, intersections, subtractions, and xors of intervals (gaps)."""
from .gaps import Endpoint, Gaps, NegativeInfinity, PositiveInfinity
from .var import x

__all__ = [
    "Endpoint",
    "Gaps",
    "NegativeInfinity",
    "PositiveInfinity",
    "x",
]

__version__ = "0.2.1"
