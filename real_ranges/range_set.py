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


class RangeSet:
    """A collection of mutually disjoint Ranges."""
    def __init__(self, *ranges):
        self._ranges = []
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
        other_ranges = iter(other)
        other_range = next(other_ranges, None)

        self_ranges = iter(self)
        self_range = next(self_ranges, None)

        anded_ranges = []
        while other_range and self_range:
            if self_range.intersects(other_range):
                anded_ranges.append(self_range & other_range)

            if self_range.upper < other_range.upper:
                self_range = next(self_ranges, None)
            else:
                other_range = next(other_ranges, None)

        s = RangeSet()
        s._ranges = anded_ranges
        return s

    @ensure_type
    def __or__(self, other):
        """Similar to __and__ and __xor__ this implementation of __or__ is O(n + m),
        where n = len(self) and m = len(other). Note that __ior__ is O(m log n).
        """
        other_ranges = iter(other)
        other_range = next(other_ranges, None)

        self_ranges = iter(self)
        self_range = next(self_ranges, None)

        unioned_ranges = []
        while other_range and self_range:
            if self_range.will_join(other_range):
                if self_range.upper == other_range.upper:
                    unioned_ranges.append(self_range | other_range)
                    other_range = next(other_ranges, None)
                    self_range = next(self_ranges, None)
                elif other_range.upper < self_range.upper:
                    self_range |= other_range
                    other_range = next(other_ranges, None)
                else:
                    other_range |= self_range
                    self_range = next(self_ranges, None)
            elif other_range.end < self_range:
                unioned_ranges.append(other_range)
                other_range = next(other_ranges, None)
            else:
                unioned_ranges.append(self_range)
                self_range = next(self_ranges, None)

        if other_range:
            unioned_ranges.append(other_range)
            unioned_ranges.extend(other_ranges)
        elif self_range:
            unioned_ranges.append(self_range)
            unioned_ranges.extend(self_ranges)

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
        other_ranges = iter(other)
        other_range = next(other_ranges, None)

        self_ranges = iter(self)
        self_range = next(self_ranges, None)

        xored_ranges = []
        while other_range and self_range:
            if self_range.will_join(other_range):
                dif = self_range ^ other_range
                if isinstance(dif, RangeBase):
                    if other_range.upper == self_range.upper:
                        if dif:
                            xored_ranges.append(dif)
                        other_range = next(other_ranges, None)
                        self_range = next(self_ranges, None)
                    elif other_range.upper < self_range.upper:
                        self_range = dif
                        other_range = next(other_ranges, None)
                    else:
                        other_range = dif
                        self_range = next(self_ranges, None)
                else:
                    r1, r2 = dif
                    xored_ranges.append(r1)
                    if other_range.end < self_range.end:
                        self_range = r2
                        other_range = next(other_ranges, None)
                    else:
                        other_range = r2
                        self_range = next(self_ranges, None)
            elif other_range.end < self_range:
                xored_ranges.append(other_range)
                other_range = next(other_ranges, None)
            else:
                xored_ranges.append(self_range)
                self_range = next(self_ranges, None)

        if other_range:
            xored_ranges.append(other_range)
            xored_ranges.extend(other_ranges)
        elif self_range:
            xored_ranges.append(self_range)
            xored_ranges.extend(self_ranges)

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

    def __repr__(self):
        return f'{{{", ".join(map(str, self._ranges))}}}'