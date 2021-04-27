from bisect import bisect

from .ranges import Range, RangeSet


class RangeDict:
    """
    RangeDicts allows one to map a continous range of keys to a value.  Ranges in RangeDicts must be mutually disjoint.
    Given a key, the dict is searched quickly with the bisect module, so it's a reasonably fast implementation.

    Example
    -------
    ```py
    In [1]: from real_ranges import *

    In [2]: Grades = RangeDict({Range('[90, 100]'): 'A',
    ...:                     Range[80: 90]: 'B',
    ...:                     Range[70: 80]: 'C',
    ...:                     Range[60: 70]: 'D',
    ...:                     Range[0: 60]: 'F'})
    ...: Grades[90]
    Out[2]: 'A'

    In [3]: Grades[85]
    Out[3]: 'B'

    In [4]: Grades[56]
    Out[4]: 'F'
    ```
    """
    def __init__(self, items=None):
        self._ranges = []
        self._dict = {}

        if items is not None:
            if isinstance(items, dict):
                items = items.items()
            for key, value in items:
                self[key] = value

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

    def __setitem__(self, key, value):
        """Keep ranges sorted as we insert them. Raise ValueError if key is not disjoint to its neighbors.
        """
        if isinstance(key, RangeSet):
            for range_ in key:
                self.__setitem__(range_, value)
            return

        if not isinstance(key, Range) or key.is_empty:
            raise TypeError('key must be a non-empty Range')

        if key not in self._dict:
            i = bisect(self._ranges, key)

            for n in i, i - 1:
                try:
                    if self._ranges[n].intersects(key):
                        raise ValueError(f'{key} is not disjoint from other Ranges')
                except IndexError:
                    pass

            self._ranges.insert(i, key)

        self._dict[key] = value

    def __getitem__(self, key):
        """Binary search the ranges for one that may contain the key.
        """
        ranges = self._ranges

        i = bisect(ranges, key) - 1
        try:
            if key in ranges[i]:
                return self._dict[ranges[i]]
        except IndexError:
            pass

        raise KeyError(key)

    def __delitem__(self, key):
        if key not in self._dict:
            raise KeyError(key)

        del self._dict[key]

        i = bisect(self._ranges, key) - 1
        del self._ranges[i]

    def __repr__(self):
        return f'{self.__class__.__name__}({self._dict})'

    def __str__(self):
        return f'{{{", ".join(f"{range_}: {val}" for range_, val in self.items())}}}'


class DomainError(Exception):
    pass


class Piecewise(RangeDict):
    """
    A dispatch-dict that will call the correct function with a given key, e.g.:
    ```
    In [7]: f = Piecewise({Range[:4]: lambda x: 2 * x,
        ...:               Range[4:]: lambda x: 2 + x})

    In [8]: f(3)
    Out[8]: 6
    ```
    """
    def __call__(self, key):
        try:
            func = self[key]
        except KeyError as e:
            raise DomainError(f'{key} not in domain') from e
        else:
            return func(key)
