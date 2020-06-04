from bisect import bisect
from functools import wraps

from .bases import RangeBase, EMPTY_RANGE
from . import ranges as r


def ensure_type(func):
    """Convert Ranges to RangeSets"""
    @wraps(func)
    def wrapper(self, other):
        if isinstance(other, RangeBase):
            other = RangeSet(other)
        elif not isinstance(other, RangeSet):
            return NotImplemented
        return func(self, other)
    return wrapper

def replace_least_upper(self_set, other_set):
    """A helper iterator for the __and__, __or__, and __xor__ methods of RangeSet, this will call next
    on the correct RangeSet iterator (the one that last yielded the range with the least `upper` bound).
    This incurs some overhead, as we repeat comparisons, but it hopefully makes RangeSet dunders easier to
    follow.
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
        self._ranges = []
        if fast:
            self._ranges.extend(ranges)
        else:
            for range_ in ranges:
                self.add(range_)

    def add(self, range_):
        """Keep ranges sorted as we add them, and merge intersecting ranges."""
        if range_ is EMPTY_RANGE:
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

        if isinstance(other, RangeBase):
            if other is EMPTY_RANGE:
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

    def __eq__(self, other):
        return self._ranges == other._ranges

    def __hash__(self):
        """Warning: this hash is provided only as a convenience for constructing RangeDicts -- Depending on it
        for normal dicts not recommended as all RangeSets will be placed in the same bucket.
        """
        return hash(1)

    @ensure_type
    def __and__(self, other):
        iter_ranges = replace_least_upper(self, other)
        self_range, other_range = next(iter_ranges)

        anded_ranges = []
        while self_range and other_range:
            if self_range.intersects(other_range):
                anded_ranges.append(self_range & other_range)

            self_range, other_range = next(iter_ranges)

        s = RangeSet()
        s._ranges = anded_ranges
        return s

    @ensure_type
    def __or__(self, other):
        """Similar to __and__ and __xor__ this implementation of __or__ is O(n + m),
        where n = len(self) and m = len(other). Note that __ior__ is O(m log n).
        """
        iter_ranges = replace_least_upper(self, other)
        self_range, other_range = next(iter_ranges)

        unioned_ranges = []
        while self_range and other_range:
            if self_range.will_join(other_range):
                if self_range.upper == other_range.upper:
                    unioned_ranges.append(self_range | other_range)
                else:
                    iter_ranges.send(self_range | other_range)
            else:
                unioned_ranges.append(min(self_range, other_range))

            self_range, other_range = next(iter_ranges)

        unioned_ranges.extend(iter_ranges)

        s = RangeSet()
        s._ranges = unioned_ranges
        return s

    @ensure_type
    def __ior__(self, other):
        for range_ in other:
            self.add(range_)
        return self

    @ensure_type
    def __xor__(self, other):
        iter_ranges = replace_least_upper(self, other)
        self_range, other_range = next(iter_ranges)

        xored_ranges = []
        while self_range and other_range:
            if self_range.will_join(other_range):
                dif = self_range ^ other_range
                if isinstance(dif, RangeSet):
                    r, dif = dif
                    xored_ranges.append(r)

                if self_range.upper == other_range.upper:
                    if dif:
                        xored_ranges.append(dif)
                else:
                    iter_ranges.send(dif)
            else:
                xored_ranges.append(min(self_range, other_range))

            self_range, other_range = next(iter_ranges)

        xored_ranges.extend(iter_ranges)

        s = RangeSet()
        s._ranges = xored_ranges
        return s

    def __len__(self):
        return len(self._ranges)

    def __invert__(self):
        return self ^ r.BIG_RANGE

    @ensure_type
    def __sub__(self, other):
        return self & ~other

    def copy(self):
        s = RangeSet()
        s._ranges = self._ranges.copy()
        return s

    @property
    def measure(self):
        return sum(r.measure for r in self._ranges)

    def map(self, func):
        return RangeSet(*(r.map(func) for r in self._ranges))

    def __repr__(self):
        return f'{{{", ".join(map(str, self._ranges))}}}'