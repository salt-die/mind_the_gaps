from bisect import bisect
from contextlib import suppress

from .ranges import Range
from .range_set import RangeSet


class RangeDict:
    def __init__(self, items=None):
        self._ranges = []
        self._range_to_value = {}

        if items is not None:
            if isinstance(items, dict):
                items = items.items()
            for key, value in items:
                self[key] = value


    def __setitem__(self, key, value):
        """Keep ranges sorted as we insert them. Raise ValueError if key is not disjoint to its neighbors.
        """
        if isinstance(key, RangeSet):
            for range_ in key:
                self.__setitem__(range_, value)
            return

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
        ranges = self._ranges

        i = bisect(ranges, key) - 1
        with suppress(IndexError):
            if key in ranges[i]:
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


class DomainError(Exception):
    pass


class Piecewise(RangeDict):
    """A dispatch-dict that will call the correct function with a given key, e.g.:
        ```
        In [7]: f = Piecewise({Range[:4]: lambda x: 2 * x,
           ...:                Range[4:]: lambda x: 2 + x})

        In [8]: f(3)
        Out[8]: 6
        ```
    """
    def __call__(self, key):
        try:
            func = super().__getitem__(key)
            return func(key)
        except KeyError:
            raise DomainError(f'{key} not in domain')
