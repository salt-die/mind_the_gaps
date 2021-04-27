#real_ranges
------------

A faster continous range implementation! We've implemented both continuous `Range`s and sets of non-contiguous ranges (`RangeSet`s).
Since `RangeSet`s keep ranges sorted as they're added, we can do set operations in linear time ( O(n + m) ), much faster than usual O(n * m) operations.
(Note that creating a `RangeSet` is O(n log n) in general, but linear if our ranges are already sorted.)

Construct `Range`s from:
| strings| slices | default|
| --- | --- | --- |
|`Range('[0, 1)')`| `Range[3:5]`|`Range(4.5, 35, start_inc=False, end_inc=True)`|

(`start_inc=True`, `end_inc=False` are default)
Range's start and end can be anything that's comparable with `<`, `>`.
```
Implemented operations include:  & Intersection
                                 | Union
                                 ^ Symmetric Difference
                                 ~ Inversion
                                 - Difference
```

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
   ...: print(work_day - bob_meeting_times - sue_meeting_times)
   ...:
{[08:00:00, 08:30:00), [09:30:00, 10:00:00), [10:30:00, 11:00:00), [16:00:00, 17:00:00)}
```
And there you go!  We know exactly which times Bob and Sue could meet!
