Continuous Ranges

Yet another continous range implementation.  Construct ranges from strings: `Range('[0, 1)')`, from slices:
`Range[3:5]`, or just normally `Range(4.5, 35, start_inc=False, end_inc=True)`.  If one doesn't specify whether
the start or end is included or not, the default is a half-open interval: start included, end excluded.

Implemented operations include:  | Union
                                 & Intersection
                                 ^ Symmetric Difference
                                 ~ Inversion
                                 - Difference

Range start and end can be anything that's comparable with `<`, `>`.  Also returns a valid length
for anything with `__sub__` defined.

RangeSets have most the same operations defined as Ranges, but allow non-contiguous groups of Ranges.

RangeDicts allows one to map a continous range of keys to a value.  Ranges in RangeDicts must be mutually disjoint.
Given a key, the dict is searched quickly with the bisect module, so it's a reasonably fast implementation.

We've intentionally left out a lot of Error Catching to make the code easier to grok.  Onus is on the user to not
break things.