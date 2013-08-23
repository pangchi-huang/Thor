#!/usr/bin/env python

# standard library imports

# third party related imports
from pyspecs import and_, given, the, then, when

# local library imports
from Thor.utils.Interval import Interval, IntervalList


with given.some_intervals:

    with when.two_intervals_are_joint:
        i = Interval(0, 10)
        j = Interval(10, 20)
        interval_list = IntervalList(i, j)

        with then.two_intervals_can_be_merged:
            the(len(interval_list)).should.equal(1)

        with and_.the_begin_of_merged_interval_is_correct:
            the(interval_list[0].begin).should.equal(0)

        with and_.the_end_of_merged_interval_is_correct:
            the(interval_list[0].end).should.equal(20)

    with when.intervals_can_be_merged:
        i = Interval(0, 10)
        j = Interval(15, 20)
        k = Interval(9, 11)
        interval_list = IntervalList(i, j, k)

        the(len(interval_list)).should.equal(2)
        the(interval_list[0]).should.equal(Interval(0, 11))
        the(interval_list[1]).should.equal(Interval(15, 20))

    with when.intervlas_cannot_be_merged:
        i = Interval(40, 50)
        j = Interval(20, 30)
        k = Interval(0, 10)
        interval_list = IntervalList(i, j, k)

        with then.len_of_interval_list_is_the_number_of_intervals:
            the(len(interval_list)).should.equal(3)

        with and_.intervals_are_sorted:
            the(interval_list[0]).should.equal(k)
            the(interval_list[1]).should.equal(j)
            the(interval_list[2]).should.equal(i)


with given.interval_list_contains_no_interval:

    with then.there_is_no_gap_of_cource:
        the(len(IntervalList().gaps)).should.equal(0)


with given.some_intervals:

    with when.two_intervals_are_joint:
        i = Interval(0, 10)
        j = Interval(10, 20)
        interval_list = IntervalList(i, j)

        with then.there_is_no_gap:
            the(len(interval_list.gaps)).should.equal(0)

    with then.gaps_are_correctly_found:
        i = Interval(40, 50)
        j = Interval(20, 30)
        k = Interval(0, 10)
        interval_list = IntervalList(i, j, k)
        gaps = interval_list.gaps

        the(len(gaps)).should.equal(2)
        the(gaps[0]).should.equal(Interval(10, 20))
        the(gaps[1]).should.equal(Interval(30, 40))
