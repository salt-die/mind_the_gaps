"""A library for unions, intersections, subtractions, and xors of intervals (gaps)."""
from .gaps import Endpoint, Gaps, NegativeInfinity, PositiveInfinity

__all__ = ["Gaps", "PositiveInfinity", "NegativeInfinity", "Endpoint"]
__version__ = "0.2.0"
