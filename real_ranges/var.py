"""
Vars help one create ranges quickly.  One should have the order `start < Var < end` and not `end > Var > start`.
```
In [13]: x = Var('x')

In [14]: 5 <= x < 10
Out[14]: [5, 10)

In [15]: RangeSet(5 <= x < 10, 11 <= x < 12, 13 <= x < 15)
Out[15]: {[5, 10), [11, 12), [13, 15)}
```

Warning
-------
One can get unexpected errors if not careful:
```
In [16]: 2 <= x
Out[16]: [2, ∞)

In [17]: x < 10
Out[17]: [2, 10)  # Previous range's start value was stored and used to create this range

In [18]: x < 10
Out[18]: (-∞, 10)  # Start value was reset to None
```

Notes
-----
`Var` stores a range's start value in __gt__ or __ge__so that it can return the correct Range while chaining operators and
start will only be reset after a call to __lt__ or __le__.  This is necessary until Python allows rich comparison chaining instead of the current
short-circuiting behavior.
"""
from .ranges import Range, EMPTY_RANGE

class Var:
    def __init__(self, name):
        self.name = name
        self.start = None

    def __repr__(self):
        return self.name

    def __gt__(self, other):
        self.start = other
        self.start_inc = False
        return Range(other, 'inf', start_inc=False)

    def __lt__(self, other):
        if self.start is not None:
            if self.start < other or self.start == other and self.start_inc:
                r = Range(self.start, other, start_inc=self.start_inc)
            else:
                r = EMPTY_RANGE
            self.start = None
            return r
        return Range('-inf', other)

    def __ge__(self, other):
        self.start = other
        self.start_inc = True
        return Range(other)

    def __le__(self, other):
        if self.start is not None:
            if self.start < other:
                r = Range(self.start, other, start_inc=self.start_inc, end_inc=True)
            else:
                r = EMPTY_RANGE

            self.start = None
            return r

        return Range('-inf', other, end_inc=True)
