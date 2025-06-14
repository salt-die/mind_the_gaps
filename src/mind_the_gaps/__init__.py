"""A library for unions, intersections, subtractions, and xors of intervals (gaps)."""

from .gaps import Endpoint, Gaps
from .var import Var, x

__all__ = ["Endpoint", "Gaps", "Var", "x"]

__version__ = "0.5.1"
