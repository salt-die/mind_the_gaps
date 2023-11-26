from dataclasses import dataclass

from .gaps import Endpoint, SupportsLessThan

__all__ = ["x"]


@dataclass
class _Var[T: SupportsLessThan]:
    name: str

    def __str__(self):
        return self.name

    def __gt__(self, value: T) -> Endpoint:
        return Endpoint(value, "(")

    def __ge__(self, value: T) -> Endpoint:
        return Endpoint(value, "[")

    def __lt__(self, value: T) -> Endpoint:
        return Endpoint(value, ")")

    def __le__(self, value: T) -> Endpoint:
        return Endpoint(value, "]")


x = _Var("x")
"""
A very convenient constructor for `Endpoints`.

It's best to start with an example::
    >>> from mind_the_gaps import x
    >>> 0 <= x
    Endpoint(value=0, boundary='[')
    >>> x < 1
    Endpoint(value=1, boundary=')')
    >>> print(Gaps([0 <= x, x < 1]))
    {[0, 1)}

Values compared with `x` will return an endpoint. The type of comparison determines
the boundary of the endpoint. `>` is left-open, `>=` is left-closed, `<` is right-open,
and `<=` is right-closed.
"""
