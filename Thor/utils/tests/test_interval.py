#!/usr/bin/env python

# standard library imports

# third party related imports
from pyspecs import and_, given, provided, the, then, this, when

# local library imports
from Thor.utils.Interval import Interval


def intersect_interval_should_follow_spec(i, j, result):

    i = Interval(*i)
    j = Interval(*j)

    if result is None:
        this(i & j).should.be(None)
        this(j & i).should.be(None)
        return

    k = i & j
    the(k.begin).should.equal(result[0])
    the(k.end).should.equal(result[1])

    k = j & i
    the(k.begin).should.equal(result[0])
    the(k.end).should.equal(result[1])

def merged_interval_should_follow_spec(i, j, result):

    i = Interval(*i)
    j = Interval(*j)

    k = i | j
    the(k.begin).should.equal(result[0])
    the(k.end).should.equal(result[1])

    k = j | i
    the(k.begin).should.equal(result[0])
    the(k.end).should.equal(result[1])

with when.an_interval_intersects_the_other_interval:

    with provided.two_intervals_are_totally_overlapping:
        intersect_interval_should_follow_spec((0, 100), (0, 100), (0, 100))

    with provided.two_intervals_are_joint:
        intersect_interval_should_follow_spec((0, 10), (10, 20), None)

    with provided.two_intervals_have_the_same_left_tip:
        intersect_interval_should_follow_spec((0, 10), (0, 1), (0, 1))

    with provided.two_intervals_have_the_same_right_tip:
        intersect_interval_should_follow_spec((0, 10), (9, 10), (9, 10))

    with provided.one_interval_includes_the_other:
        intersect_interval_should_follow_spec((0, 10), (5, 8), (5, 8))

    with provided.two_intervals_are_partly_overlapping:
        intersect_interval_should_follow_spec((0, 10), (-5, 3), (0, 3))


with when.two_intervals_merge:

    with provided.two_intervals_are_totally_overlapping:
        merged_interval_should_follow_spec((0, 10), (0, 10), (0, 10))

    with provided.two_intervals_are_disjoint:
        merged_interval_should_follow_spec((0, 10), (15, 20), (0, 20))

    with provided.two_intervals_are_partly_overlapping:
        merged_interval_should_follow_spec((0, 10), (5, 15), (0, 15))

    with provided.one_interval_includes_the_other:
        merged_interval_should_follow_spec((0, 10), (5, 8), (0, 10))

with given.an_interval:

    i = Interval(0, 10)

    with then.the_length_should_be_correct:
        the(i.length).should.equal(10)

with given.two_intervals:

    with provided.have_the_same_left_tip_but_distince_right_tip:
        i = Interval(0, 10)
        j = Interval(0, 5)
        this(i).should_NOT.equal(j)

    with provided.have_the_same_right_tip_but_distinct_left_tip:
        i = Interval(5, 10)
        j = Interval(0, 10)
        this(i).should_NOT.equal(j)

    with provided.the_same_left_right_tips:
        i = Interval(0, 10)
        j = Interval(0, 10)
        this(i).should.equal(j)
