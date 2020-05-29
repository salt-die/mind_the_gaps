Continuous Ranges

Yet another continous range implementation.  Construct ranges from strings: `Range('[0, 1)')`, from slices:
`Range[3:5]`, or just normally `Range(4.5, 35, start_inc=False, end_inc=True)`.  If one doesn't specify whether
the start or end is included or not, the default is a half-open interval: start included, end excluded.

```
Implemented operations include:  | Union
                                 & Intersection
                                 ^ Symmetric Difference
                                 ~ Inversion
                                 - Difference
```

Range start and end can be anything that's comparable with `<`, `>`.  Also returns a valid length
for anything with `__sub__` defined.

RangeSets have most the same operations defined as Ranges, but allow non-contiguous groups of Ranges.

RangeDicts allows one to map a continous range of keys to a value.  Ranges in RangeDicts must be mutually disjoint.
Given a key, the dict is searched quickly with the bisect module, so it's a reasonably fast implementation.

We've intentionally left out a lot of Error Catching to make the code easier to grok.  Onus is on the user to not
break things.


How about a reasonable use-case for continous ranges?  Say Bob and Sue have a busy schedule with meetings throughout
the day and they'd like to know when and if they could find time for each other:

```py
In [1]: from real_ranges import *
   ...: from datetime import time
   ...:
   ...: bob_meeting_times = RangeSet(Range[time(8, 30): time(9)],
   ...:                              Range[time(11): time(12)],
   ...:                              Range[time(14): time(16)])
   ...:
   ...: sue_meeting_times = RangeSet(Range[time(8, 30): time(9, 30)],
   ...:                              Range[time(10): time(10, 30)],
   ...:                              Range[time(11): time(14, 30)])
   ...:
   ...: work_day = Range[time(8): time(17)]
   ...:
   ...: bob_free_time = bob_meeting_times ^ work_day
   ...: sue_free_time = sue_meeting_times ^ work_day
   ...:
   ...: print(bob_free_time, sue_free_time, sep='\n')
   ...:
   ...: bob_free_time & sue_free_time
{[08:00:00, 08:30:00), [09:00:00, 11:00:00), [12:00:00, 14:00:00), [16:00:00, 17:00:00)}
{[08:00:00, 08:30:00), [09:30:00, 10:00:00), [10:30:00, 11:00:00), [14:30:00, 17:00:00)}
Out[1]: {[08:00:00, 08:30:00), [09:30:00, 10:00:00), [16:00:00, 17:00:00)}
```

And there you go!  We know exactly which times Bob and Sue could meet!


Here's a simple example of a continous-range dict in action:

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

Or a piecewise dispatch-dict:
```py
In [7]: f = Piecewise({Range[:4]: lambda x: 2 * x,
   ...:                Range[4:]: lambda x: 2 + x})

In [8]: f(3), f(4)
Out[8]: (6, 6)
```