from bisect import bisect
from contextlib import suppress

from .ranges import Range


class RangeDict:
    def __init__(self, dict_=None):
        self._ranges = []
        self._range_to_value = {}

        if dict_ is not None:
            for key, value in dict_.items():
                self[key] = value

    def __setitem__(self, key, value):
        """Keep ranges sorted as we insert them. Raise ValueError if key is not disjoint to its neighbors.
        """
        if not isinstance(key, Range):
            raise TypeError('key must be a non-empty Range')

        if key not in self._range_to_value:
            i = bisect(self._ranges, key)

            for n in (i, i - 1):
                with suppress(IndexError):
                    if self._ranges[n].intersects(key):
                        raise ValueError(f'{key} is not disjoint from other Ranges')

            self._ranges.insert(i, key)

        self._range_to_value[key] = value

    def __getitem__(self, key):
        """Binary search the ranges for one that may contain the key."""
        i = bisect(self.ranges, key) - 1
        with suppress(IndexError):
            if key in self._ranges[i]:
                return self._range_to_value[ranges[i]]

        raise KeyError(key)

    def __delitem__(self, key):
        if key not in self._range_to_value:
            raise KeyError(key)

        del self._range_to_value[key]

        i = bisect(self._ranges, key) - 1
        del self._ranges[i]

    def __repr__(self):
        return f'{self.__class__.__name__}({self._range_to_value})'
