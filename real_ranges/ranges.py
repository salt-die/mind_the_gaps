from functools import wraps
from .inf import Immutable, INF
from .meta import RangeMeta
from . import range_set


class RangeBase(Immutable):
    """Range base class.
    """
    @property
    def endpoints(self):
        return self.start, self.end

    @property
    def lower(self):
        return self.start, self.start_inc

    @property
    def upper(self):
        return self.end, self.end_inc

    def __iter__(self):
        yield self.start, self.start_inc
        yield self.end, self.end_inc


class EMPTY_RANGE(RangeBase):
    start = end = None
    start_inc = end_inc = False

    @property
    def measure(self):
        return 0

    def __bool__(self):
        return False

    def __contains__(self, other):
        return False

    intersects = continues = __gt__ = __contains__

    def __lt__(self, other):
        return True

    will_join = __lt__

    def __and__(self, other):
        return self

    def __or__(self, other):
        return other

    __xor__ = __ior__ = __or__

    def __invert__(self):
        return Range()

    def __eq__(self, other):
        return other is self

    def __repr__(self):
        return '∅'


def ensure_order(func):
    """Return NotImplemented if other is not a Range; switch other, self if other < self.
    """
    @wraps(func)
    def wrapper(self, other):
        if not isinstance(other, RangeBase):
            return NotImplemented

        if other < self:
            return getattr(other, func.__name__)(self)
        return func(self, other)

    return wrapper


class Range(RangeBase, metaclass=RangeMeta):
    __slots__ = 'start', 'end', 'start_inc', 'end_inc', '_cmp', '_hash'

    def __init__(self, start=None, end=None, /, start_inc=True, end_inc=False):
        cmp = start, not start_inc, end, end_inc
        hash_ = hash(cmp)

        for name, val in zip(self.__slots__, (start, end, start_inc, end_inc, cmp, hash_)):
            super(Immutable, type(self)).__setattr__(self, name, val)

    def __bool__(self):
        return True

    def __hash__(self):
        return self._hash

    def __lt__(self, other):
        """
        Ranges are ordered by their least element first.  (With EMPTY_RANGE before everything.)
        If other is not a range, then return True if other is greater than all elements in this range.
        """
        if other is EMPTY_RANGE:
            return False

        if isinstance(other, Range):
            return self._cmp < other._cmp

        return self.end < other or not self.end_inc and self.end == other and not self.end is INF

    def __gt__(self, other):
        if other is EMPTY_RANGE:
            return True

        if isinstance(other, Range):
            return other < self

        return self.start > other or not self.start_inc and self.start == other and not self.start is -INF

    def __contains__(self, value):
        """Return true if value is in the range.
        """
        return  (
            self.start < value < self.end
            or self.start == value and self.start_inc
            or self.end == value and self.end_inc
        )

    @ensure_order
    def __eq__(self, other):
        return self._cmp == other._cmp

    @ensure_order
    def will_join(self, other):
        """Return true if the union of self and other is a single contiguous range.
        """
        return self is BIG_RANGE or other.start in self or self.end in other

    @ensure_order
    def continues(self, other):
        """
        Return true if either self.end == other.start or self.start == other.end
        and one point is inclusive and the other is exclusive.
        """
        return self.end_inc != other.start_inc and self.end == other.start

    @ensure_order
    def intersects(self, other):
        """Return true if the intersection with 'other' isn't empty.
        """
        return self.will_join(other) and not self.continues(other)

    @ensure_order
    def __and__(self, other):
        """Returns intersection of two Ranges.
        """
        if self.end > other:
            return other

        if not self.intersects(other):
            return EMPTY_RANGE

        return Range(other.start, self.end, other.start_inc, self.end_inc)

    @ensure_order
    def __or__(self, other):
        """Returns union of two Ranges.
        """
        if self.end > other:
            return self

        if not self.will_join(other):
            return range_set.RangeSet(self, other, fast=True)

        return Range(self.start, other.end, self.start_inc, other.end_inc)

    __ior__ = __or__

    @ensure_order
    def __xor__(self, other):
        """Symmetric difference of two Ranges.
        """
        if self == other:
            return EMPTY_RANGE

        if not self.intersects(other):
            return self | other

        if self.lower == other.lower:
            return Range(self.end, other.end, not self.end_inc, other.end_inc)

        if self.upper == other.upper:
            return Range(self.start, other.start, self.start_inc, not other.start_inc)

        r1 = Range(self.start, other.start, self.start_inc, not other.start_inc)
        if self.upper < other.upper:
            self, other = other, self
        r2 = Range(other.end, self.end, not other.end_inc, self.end_inc)
        return range_set.RangeSet(r1, r2, fast=True)

    def __invert__(self):
        return BIG_RANGE ^ self

    def __sub__(self, other):
        """Difference of two Ranges.
        """
        return ~other & self  # order swapped so RangeSet.__and__ is called if other is a RangeSet

    @property
    def measure(self):
        if self.start is -INF or self.end is INF:
            return float('inf')
        try:
            return self.end - self.start
        except TypeError as e:
            raise NotImplementedError(f"no __sub__ defined for type '{type(self.end).__name__}'") from e

    def map(self, func):
        """
        Returns a new range that's this range transformed by a given function.
        Only limited numerical operations supported for INF and -INF.
        """
        return Range(func(self.start), func(self.end), self.start_inc, self.end_inc)

    def __repr__(self):
        return f'{"(["[self.start_inc]}{self.start}, {self.end}{")]"[self.end_inc]}'


EMPTY_RANGE = EMPTY_RANGE()
BIG_RANGE = Range()  # The (-inf, inf) range -- it's big!
