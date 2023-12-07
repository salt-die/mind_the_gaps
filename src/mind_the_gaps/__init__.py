"""A library for unions, intersections, subtractions, and xors of intervals (gaps)."""
from .gaps import Endpoint, Gaps
from .var import x

__all__ = ["Endpoint", "Gaps", "x"]

__version__ = "0.3.0"
