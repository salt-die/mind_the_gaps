from .bases import INF
from contextlib import suppress

def from_string(str_):
    if not str_.startswith(('(', '[')) or not str_.endswith((')', ']')):
        raise ValueError

    start, end = str_[1:-1].split(',')
    start = start.strip()
    end = end.strip()
    if start == '-inf':
        start = -INF
        start_inc = False
    else:
        start = int(start) if start.isdigit() else float(start)
        start_inc = str_[0] == '['

    if end == 'inf':
        end = INF
        end_inc = False
    else:
        end = int(end) if end.isdigit() else float(end)
        end_inc = str_[-1] == ']'
    return start, end, start_inc, end_inc


class RangeMeta(type):
    """This metaclass allows Ranges to be constructed like so:
            Range[1:3] == Range(1, 3)
            Range[False, 1:3]  == Range(1, 3, start_inc=False)
            Range[1:3, True] == Range(1, 3, end_inc=True)
            Range[False, 1:3, True] == Range(1, 3, False, True)
       In general, we have Range[start_inc, start:end, end_inc] with start_inc, end_inc defaulting to True, False.
       Ellipsis and None both map to INF or -INF in slices.

    This metaclass also caches the "default" range (BIG_RANGE or (-inf, inf)) and returns it when called.
    """
    BIG_RANGE = None

    def __getitem__(cls, args):
        if isinstance(args, slice):
            return cls(args.start, args.stop)

        if not isinstance(args, tuple):
            return cls(args)

        if len(args) == 2:  # a slice and an endpoint
            if not isinstance(args[0], slice):
                return cls(args[1].start, args[1].stop, start_inc=args[0])
            return cls(args[0].start, args[0].stop, end_inc=args[1])

        return cls(args[1].start, args[1].stop, start_inc=args[0], end_inc=args[2])

    def __call__(cls, start=None, end=None, /, start_inc=True, end_inc=False):
        # Try to construct from string
        if isinstance(start, str):
            with suppress(TypeError, ValueError, IndexError):
                start, end, start_inc, end_inc = from_string(start)

        if start is None or start is ... or start == '-inf' or start is -INF:
            start = -INF
            start_inc = False
        if end is None or end is ... or end == 'inf' or end is INF:
            end = INF
            end_inc = False

        if start is -INF and end is INF:
            if RangeMeta.BIG_RANGE is None:
                RangeMeta.BIG_RANGE = super(RangeMeta, cls).__call__(start, end, start_inc, end_inc)
            return RangeMeta.BIG_RANGE

        if start > end:
            start, end = end, start
            start_inc, end_inc = end_inc, start_inc
        elif start == end:
            end_inc = True
            start_inc = True

        return super(RangeMeta, cls).__call__(start, end, start_inc, end_inc)


