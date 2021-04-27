from bisect import bisect
from functools import wraps
from types import GeneratorType

from .constants import INF, NEG_INF

def _parse_end(end):
    """Helper for `from_string`.  Determines if an endpoint is INF, NEG_INF, int, or float.
    """
    if end == 'inf':
        return INF
    if end == '-inf':
        return NEG_INF
    if end.isdigit():
        return int(end)
    return float(end)

def from_string(str_):
    """Attempts to parse a Range's `start`, `end`, `start_inc`, `end_inc` attributes from a string.
    """
    if not str_.startswith(('(', '[')) or not str_.endswith((')', ']')):
        raise ValueError

    start, end = str_[1:-1].split(',')
    start = _parse_end(start.strip())
    end = _parse_end(end.strip())

    start_inc = str_[0] == '['
    end_inc = str_[-1] == ']'

    return start, end, start_inc, end_inc

def rangeset_compatible(func):
    """If `other` is a `RangeSet`, call `other`'s method.
    """
    @wraps(func)
    def wrapper(self, other):
        if isinstance(other, RangeSet):
            return getattr(other, func.__name__)(self)
        return func(self, other)
    return wrapper

def ensure_type(func):
    """Return `NotImplemented` if `other` is not an instance of `type(self)`.
    """
    @wraps(func)
    def wrapper(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return func(self, other)
    return wrapper

def ensure_order(func):
    """Switch `other` and `self` if `other` < `self`.
    """
    @wraps(func)
    def wrapper(self, other):
        if other < self:
            return getattr(other, func.__name__)(self)
        return func(self, other)
    return wrapper


class Range:
    __slots__ = 'start', 'end', 'start_inc', 'end_inc', '_cmp', '_hash'

    def __class_getitem__(cls, args):
        """
        A very uncommon constructor! This method allows Ranges to be constructed like so:
        ┌─────────────────────────┬──────────────────────────────┐
        │ __class_getitem__       │ __init__                     │
        ├─────────────────────────┼──────────────────────────────┤
        │ Range[1:3]              │ Range(1, 3)                  │
        │ Range[False, 1:3]       │ Range(1, 3, start_inc=False) │
        │ Range[1:3, True]        │ Range(1, 3, end_inc=True)    │
        │ Range[False, 1:3, True] │ Range(1, 3, False, True)     │
        └─────────────────────────┴──────────────────────────────┘

        In general, we have Range[start_inc, start:end, end_inc] with start_inc, end_inc defaulting to True, False.

        Notes
        -----
        Ellipsis and None both map to INF or NEG_INF in slices.

        Warning
        -------
        Raises ValueError if slice has a non-None `step`.
        """
        if isinstance(args, slice):
            if args.step != None:
                raise ValueError(f"Can't interpret {args!r} step")
            return cls(args.start, args.stop)

        if not isinstance(args, tuple):
            return cls(args)

        if len(args) == 2:  # a slice and an endpoint
            if not isinstance(args[0], slice):
                return cls(args[1].start, args[1].stop, start_inc=args[0])
            return cls(args[0].start, args[0].stop, end_inc=args[1])

        return cls(args[1].start, args[1].stop, start_inc=args[0], end_inc=args[2])

    def __init__(self, start=None, end=None, /, start_inc=True, end_inc=False):
        if isinstance(start, str):
            try:
                start, end, start_inc, end_inc = from_string(start)
            except (TypeError, ValueError, IndexError):
                pass

        if start in (None, ..., '-inf'):
            start = NEG_INF

        if end in (None, ..., 'inf'):
            end = INF

        self.start = start
        self.end = end
        self.start_inc = start_inc
        self.end_inc = end_inc
        self._cmp = start, not start_inc, end, end_inc
        self._hash = None

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
        yield self.lower
        yield self.upper

    @property
    def is_empty(self):
        return not (
            self.start < self.end or  # normal case
            self.start == self.end and self.start_inc == self.end_inc == True  # degenerate case (singleton)
        )

    def __bool__(self):
        return not self.is_empty

    @property
    def is_degenerate(self):
        """A Range is degenerate if it only contains a single value.
        """
        return self.start == self.end and self.start_inc == self.end_inc == True

    @property
    def is_big(self):
        """Returns true if start is `NEG_INF` and end is `INF`.
        """
        return self.start is NEG_INF and self.end is INF

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(self._cmp)
        return self._hash

    def __lt__(self, other):
        """
        Ranges are ordered by their least element first.

        Notes
        -----
        This operator is overloaded; for non-Ranges this returns True if `other` is greater than all elements in this range.
        """
        if isinstance(other, Range):
            return self._cmp < other._cmp

        return self.end < other or not self.end_inc and self.end == other and not self.end is INF

    def __gt__(self, other):
        """
        Ranges are ordered by their least element first.

        Notes
        -----
        This operator is overloaded; for non-Ranges this returns True if `other` is less than all elements in this range.
        """
        if isinstance(other, Range):
            return other < self

        return self.start > other or not self.start_inc and self.start == other and not self.start is NEG_INF

    def __contains__(self, value):
        """Returns True if value is in the range.
        """
        if self.is_empty:
            return False

        if self.is_degenerate:
            return self.value == self.start

        return  (
            self.start < value < self.end
            or self.start == value and self.start_inc
            or self.end == value and self.end_inc
        )

    @rangeset_compatible
    @ensure_type
    @ensure_order
    def __eq__(self, other):
        """Ranges are equal if they contain the same members.
        """
        return self.is_empty and other.is_empty or self._cmp == other._cmp

    @ensure_type
    @ensure_order
    def will_join(self, other):
        """Return true if the union of self and other is a single contiguous range.
        """
        return self.is_big or other.start in self or self.end in other

    @ensure_type
    @ensure_order
    def continues(self, other):
        """
        Return true if either self.end == other.start or self.start == other.end
        and one point is inclusive and the other is exclusive.
        """
        return self.end_inc != other.start_inc and self.end == other.start

    @rangeset_compatible
    @ensure_type
    @ensure_order
    def intersects(self, other):
        """Return true if the intersection with 'other' isn't empty.
        """
        return self.will_join(other) and not self.continues(other)

    @rangeset_compatible
    @ensure_type
    @ensure_order
    def __and__(self, other):
        """Returns intersection of two Ranges.
        """
        if self.end > other:
            return other

        return Range(other.start, self.end, other.start_inc, self.end_inc)  # This might be an empty range

    @rangeset_compatible
    @ensure_type
    @ensure_order
    def __or__(self, other):
        """Returns union of two Ranges.
        """
        if self.end > other:
            return self

        if not self.will_join(other):
            return RangeSet(self, other, fast=True)

        return Range(self.start, other.end, self.start_inc, other.end_inc)

    __ior__ = __or__

    @rangeset_compatible
    @ensure_type
    @ensure_order
    def __xor__(self, other):
        """Symmetric difference of two Ranges.
        """
        if self == other:
            return RangeSet()  # It's not clear which empty Range we should return, so we return an empty RangeSet

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
        return RangeSet(r1, r2, fast=True)

    def __sub__(self, other):
        """Difference of two Ranges.
        """
        return self & ~other  # Because we'd have to swap the operands, we avoid decorating this method
                              # and piggy-back off the decorators on the other overloaded methods.

    def __invert__(self):
        return Range() ^ self

    @property
    def measure(self):
        if self.is_empty:
            return 0

        if self.start is NEG_INF or self.end is INF:
            return float('inf')

        return self.end - self.start

    def map(self, func):
        """
        Returns a new range that's this range transformed by a given function.
        """
        return Range(func(self.start), func(self.end), self.start_inc, self.end_inc)

    def __repr__(self):
        return f'{type(self).__name__}({self.start}, {self.end}, start_inc={self.start_inc}, end_inc={self.end_inc})'

    def __str__(self):
        return f'{"(["[self.start_inc]}{self.start}, {self.end}{")]"[self.end_inc]}'


def convert_range_to_rangeset(func):
    """If `other` is a `Range`, convert to `RangeSet`.
    """
    @wraps(func)
    def wrapper(self, other):
        if isinstance(other, Range):
            other = RangeSet(other)
        return func(self, other)
    return wrapper

def _replace_least_upper(self_set, other_set):
    """
    A helper iterator for the __and__, __or__, and __xor__ methods of RangeSet, this will call next
    on the correct RangeSet iterator (the one that last yielded the range with the least `upper` bound).
    """
    self_ranges = iter(self_set)
    other_ranges = iter(other_set)

    self_range = next(self_ranges, None)
    other_range = next(other_ranges, None)

    carry_over = yield self_range, other_range

    while self_range and other_range:
        if self_range.upper == other_range.upper:
            self_range = next(self_ranges, None)
            other_range = next(other_ranges, None)
        elif self_range.upper < other_range.upper:
            self_range = next(self_ranges, None)
            if carry_over:
                other_range = carry_over
                yield
        else:
            other_range = next(other_ranges, None)
            if carry_over:
                self_range = carry_over
                yield

        carry_over = yield self_range, other_range

    if self_range:
        yield self_range
        yield from self_ranges
    elif other_range:
        yield other_range
        yield from other_ranges


class RangeSet:
    """A collection of mutually disjoint Ranges. Use `fast=True` only if ranges are already sorted and disjoint.
    """
    def __init__(self, *ranges, fast=False):
        if ranges and isinstance(ranges[0], GeneratorType):
            ranges = ranges[0]

        if fast:
            self._ranges = [range_ for range_ in ranges if not range_.is_empty]
        else:
            self._ranges = []
            for range_ in ranges:
                self.add(range_)

    def add(self, range_):
        """Keep ranges sorted as we add them, and merge intersecting ranges.
        """
        if not isinstance(range_, Range):
            return NotImplemented

        if range_.is_empty:
            return

        ranges = self._ranges

        start = bisect(ranges, range_.start)
        end = bisect(ranges, range_.end)

        if start and range_.will_join(ranges[start - 1]):
            range_ |= ranges[start - 1]
            start -= 1

        if end < len(ranges) and range_.continues(ranges[end]):
            range_ |= ranges[end]
            end += 1
        elif end and range_.will_join(ranges[end - 1]):
            range_ |= ranges[end - 1]

        if start == end:
            ranges.insert(start, range_)
        else:
            ranges[start: end] = [range_]

    def __iter__(self):
        yield from self._ranges

    def __bool__(self):
        return bool(self._ranges)

    def __contains__(self, other):
        ranges = self._ranges

        if isinstance(other, Range):
            if other.is_empty:
                return True

            i = bisect(ranges, other.start) - 1
            try:
                return other == ranges[i]
            except IndexError:
                return False

        i = bisect(ranges, other) - 1
        try:
            return other in ranges[i]
        except IndexError:
            return False

    @convert_range_to_rangeset
    @ensure_type
    def __eq__(self, other):
        return self._ranges == other._ranges

    def __hash__(self):
        """
        Warning
        -------
        RangeSets are mutable, so hashes are based on identity only.
        """
        return hash(id(self))

    @convert_range_to_rangeset
    @ensure_type
    def intersects(self, other):
        iter_ranges = _replace_least_upper(self, other)
        self_range, other_range = next(iter_ranges)

        while self_range and other_range:
            if self_range.intersects(other_range):
                return True
            self_range, other_range = next(iter_ranges)

        return False

    @convert_range_to_rangeset
    @ensure_type
    def __and__(self, other):
        iter_ranges = _replace_least_upper(self, other)
        self_range, other_range = next(iter_ranges)

        intersection = []
        while self_range and other_range:
            if self_range.intersects(other_range):
                intersection.append(self_range & other_range)

            self_range, other_range = next(iter_ranges)

        s = RangeSet()
        s._ranges = intersection
        return s

    @convert_range_to_rangeset
    @ensure_type
    def __or__(self, other):
        iter_ranges = _replace_least_upper(self, other)
        self_range, other_range = next(iter_ranges)

        union = []
        while self_range and other_range:
            if self_range.will_join(other_range):
                if self_range.upper == other_range.upper:
                    union.append(self_range | other_range)
                else:
                    iter_ranges.send(self_range | other_range)
            else:
                union.append(min(self_range, other_range))

            self_range, other_range = next(iter_ranges)

        union.extend(iter_ranges)

        s = RangeSet()
        s._ranges = union
        return s

    @convert_range_to_rangeset
    @ensure_type
    def __ior__(self, other):
        for range_ in other:
            self.add(range_)
        return self

    @convert_range_to_rangeset
    @ensure_type
    def __xor__(self, other):
        iter_ranges = _replace_least_upper(self, other)
        self_range, other_range = next(iter_ranges)

        symmetric_difference = []
        while self_range and other_range:
            if self_range.will_join(other_range):
                dif = self_range ^ other_range
                if isinstance(dif, RangeSet):
                    r, dif = dif
                    symmetric_difference.append(r)

                if self_range.upper == other_range.upper:
                    if dif:
                        symmetric_difference.append(dif)
                else:
                    iter_ranges.send(dif)
            else:
                symmetric_difference.append(min(self_range, other_range))

            self_range, other_range = next(iter_ranges)

        symmetric_difference.extend(iter_ranges)

        s = RangeSet()
        s._ranges = symmetric_difference
        return s

    def __len__(self):
        return len(self._ranges)

    def __invert__(self):
        return self ^ Range()

    @convert_range_to_rangeset
    @ensure_type
    def __sub__(self, other):
        return self & ~other

    def copy(self):
        s = RangeSet()
        s._ranges = self._ranges.copy()
        return s

    @property
    def measure(self):
        return sum(range_.measure for range_ in self._ranges)

    def map(self, func):
        return RangeSet(range_.map(func) for range_ in self._ranges)

    def __repr__(self):
        return f'{type(self).__name__}({{{", ".join(repr(range_) for range_ in self._ranges)}}})'

    def __str__(self):
        if not self._ranges:
            return '{∅}'
        return f'{{{", ".join(map(str, self._ranges))}}}'
