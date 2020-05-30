from bisect import bisect
from functools import wraps

from .bases import RangeBase, EMPTY_RANGE
from . import ranges as r


def ensure_type(func):
    """Convert Ranges to RangeSets"""
    @wraps(func)
    def wrapper(self, other):
        if isinstance(other, r.Range):
            other = RangeSet(other)
        if not isinstance(other, RangeSet):
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

        s = RangeSet()
        while other_range and self_range:
            if self_range.intersects(other_range):
                s.add(self_range & other_range)
            elif other_range.end < self_range:
                other_range = next(other_ranges, None)
                continue
            self_range = next(self_ranges, None)

        return s

    @ensure_type
    def __or__(self, other):
        s = self.copy()
        for range_ in other:
            s.add(range_)
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

        s = RangeSet()
        while other_range and self_range:
            if self_range.intersects(other_range):
                dif = self_range ^ other_range
                # Case 1: dif is a single contiguous range
                #    This indicates that the ranges share at least one endpoint.
                #    Case 1a:
                #       ranges are equal or have equal `end`s
                #    Case 1b:
                #       `start`s are equal, but other_range < self_range
                #    Case 1c:
                #       `start's are equal, but self_range < other_range
                # Case 2: dif is a RangeSet with two Ranges
                #    Ranges do not share an endpoint, but intersect.
                #    Case 2a:
                #        other_range ends before self_range
                #    Case 2b:
                #        self_range ends before other_range
                if isinstance(dif, RangeBase):
                    # 1a
                    if dif is EMPTY_RANGE \
                      or other_range.end == self_range.end and other_range.end_inc == self_range.end_inc:
                        s |= dif
                        other_range = next(other_ranges, None)
                        self_range = next(self_ranges, None)
                        continue
                    # 1b
                    if other_range < self_range:
                        self_range = dif
                        other_range = next(other_ranges, None)
                        continue
                    # 1c
                    other_range = dif
                    self_range = next(self_ranges, None)
                    continue

                r1, r2 = dif
                s |= r1
                # 2a
                if other_range.end < self_range.end:
                    self_range = r2
                    other_range = next(other_ranges, None)
                    continue
                # 2b
                other_range = r2
                self_range = next(self_ranges, None)
                continue

            if other_range.end < self_range:
                s |= other_range
                other_range = next(other_ranges, None)
                continue

            s |= self_range
            self_range = next(self_ranges, None)

        # Collect left-overs
        if other_range:
            s |= other_range
            s |= RangeSet(*other_ranges)
        elif self_range:
            s |= self_range
            s |= RangeSet(*self_ranges)
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