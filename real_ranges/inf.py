class ImmutableError(Exception):
    pass


class Immutable:
    def __setattr__(self, attr, value):
        raise ImmutableError(f"cannot assign to '{attr}'")


class INF(Immutable):
    """INF and -INF are defined to allow infinite values for non-float, non-integer types."""
    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return other is not self

    def __neg__(self):
        return MINUS_INF

    def __repr__(self):
        return '∞'

    def __hash__(self):
        return hash(float('inf'))

    def __add__(self, other):
        return self

    __sub__ = __radd__ = __add__

    def __rsub__(self, other):
        return -INF

    def __mul__(self, other):
        if other > 0:
            return self
        if other < 0:
            return -INF
        return 0

    __rmul__ = __mul__

    def __truediv__(self, other):
        if other > 0:
            return self
        if other < 0:
            return -INF
        raise ZeroDivisionError

    def __rtruediv__(self, other):
        return 0


class MINUS_INF(Immutable):
    def __lt__(self, other):
        return other is not self

    def __gt__(self, other):
        return False

    def __neg__(self):
        return INF

    def __repr__(self):
        return '-∞'

    def __hash__(self):
        return hash(-float('inf'))

    def __add__(self, other):
        return self

    __sub__ = __radd__ = __add__

    def __rsub__(self, other):
        return INF

    def __mul__(self, other):
        if other > 0:
            return self
        if other < 0:
            return INF
        return 0

    __rmul__ = __mul__

    def __truediv__(self, other):
        if other > 0:
            return self
        if other < 0:
            return INF
        raise ZeroDivisionError

    def __rtruediv__(self, other):
        return 0


INF = INF()
MINUS_INF = MINUS_INF()
