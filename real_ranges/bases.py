class ImmutableError(Exception):
    pass


class Immutable:
    def __setattr__(self, attr, value):
        raise ImmutableError(f"cannot assign to '{attr}'")


class RangeBase(Immutable):
    """Annotative base class."""


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


INF = INF()


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


MINUS_INF = MINUS_INF()


class EMPTY_RANGE(RangeBase):
    def __contains__(self, other):
        return False

    def intersects(self, other):
        return False

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return True

    def __and__(self, other):
        return self

    def __or__(self, other):
        return other

    def __xor__(self, other):
        return other

    def __invert__(self):
        return Range()

    def __len__(self):
        return 0

    def __bool__(self):
        return False

    def __repr__(self):
        return '∅'


EMPTY_RANGE = EMPTY_RANGE()