class _Inf:
    """
    This implementation of infinity is similar to `float('inf')`, except its operators allow non-numeric types.
    """
    __slots__ = ()

    def __eq__(self, other):
        return other is self

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return other is self

    def __gt__(self, other):
        return other is not self

    def __ge__(self, other):
        return True

    def __neg__(self):
        return NEG_INF

    def __repr__(self):
        return 'INF'

    def __str__(self):
        return '∞'

    def __hash__(self):
        return hash(float('inf'))

    def __add__(self, other):
        return NAN if other is NEG_INF else self

    __sub__ = __radd__ = __add__

    def __rsub__(self, other):
        return NAN if other is self else NEG_INF

    def __mul__(self, other):
        if other > 0:
            return self
        if other < 0:
            return NEG_INF
        return 0

    __rmul__ = __mul__

    def __truediv__(self, other):
        if other is self or other is NEG_INF:
            return NAN
        if other > 0:
            return self
        if other < 0:
            return NEG_INF
        raise ZeroDivisionError

    def __rtruediv__(self, other):
        if other is self or other is NEG_INF:
            return NAN
        return 0


class _NegInf:
    """
    This implementation of negative infinity is similar to `-float('inf')`, except its operators allow non-numeric types.
    """
    __slots__ = ()

    def __eq__(self, other):
        return other is self

    def __lt__(self, other):
        # We try other's `__lt__` for convenience of our `Var` class.
        try:
            return other > self
        except TypeError:
            return other is not self

    def __le__(self, other):
        # We try other's `__le__` for convenience of our `Var` class.
        try:
             return other >= self
        except TypeError:
            return True

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return other is self

    def __neg__(self):
        return INF

    def __repr__(self):
        return 'NEG_INF'

    def __str__(self):
        return '-∞'

    def __hash__(self):
        return hash(-float('inf'))

    def __add__(self, other):
        return NAN if other is INF else self

    __sub__ = __radd__ = __add__

    def __rsub__(self, other):
        return NAN if other is self else INF

    def __mul__(self, other):
        if other > 0:
            return self
        if other < 0:
            return INF
        return 0

    __rmul__ = __mul__

    def __truediv__(self, other):
        if other is self or other is INF:
            return NAN
        if other > 0:
            return self
        if other < 0:
            return INF
        raise ZeroDivisionError

    def __rtruediv__(self, other):
        if other is self or other is INF:
            return NAN
        return 0


class _Nan:
    """
    This implementation of nan is similar to `float('nan')`, except its operators allow non-numeric types.
    """
    __slots__ = ()

    def __eq__(self, other):
        return False

    __gt__ = __ge__ = __le__ = __lt__ = __eq__

    def __neg__(self):
        return self

    def __repr__(self):
        return 'NAN'

    def __hash__(self):
        return hash(float('nan'))

    def __add__(self, other):
        return self

    __sub__ = __rsub__ = __mul__ = __rmul__ = __rtruediv__ = __radd__ = __add__

    def __truediv__(self, other):
        if other == 0:
            raise ZeroDivisionError
        return self


INF = _Inf()         # These special infinities allow comparison with non-numeric types...
NEG_INF = _NegInf()  #...
NAN = _Nan()         #... and this `not a number` also allows comparison with non-numeric types.