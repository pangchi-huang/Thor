#!/usr/bin/env python

# standard library imports
import random

# third party related imports
from pyspecs import and_, given, provided, the, then, this, when

# local library imports
from Thor.utils.Point import Point


with given.two_random_points:

    p1 = Point(random.randint(0, 65536), random.randint(0, 65536))
    p2 = Point(random.randint(0, 65536), random.randint(0, 65536))

    with when.one_point_adds_the_other:
        p3 = p1 + p2

        with then.x_coordinate_should_be_correctly_calculated:
            the(p3.x).should.equal(p1.x + p2.x)

        with then.y_coordinate_should_be_correctly_calculated:
            the(p3.y).should.equal(p1.y + p2.y)

    with when.one_point_subtracts_the_other:
        p3 = p1 - p2

        with then.x_coordinate_should_be_correctly_calculated:
            the(p3.x).should.equal(p1.x - p2.x)

        with then.y_coordinate_should_be_correctly_calculated:
            the(p3.y).should.equal(p1.y - p2.y)

    with when.negative_a_point:
        p3 = -p1

        with then.x_coordinate_should_be_correctly_calculated:
            the(p3.x).should.equal(-p1.x)

        with then.y_coordinate_should_be_correctly_calculated:
            the(p3.y).should.equal(-p1.y)

    with when.calculate_square_distance:

        with provided.the_other_point_is_not_given:
            with then.the_result_is_exactly_the_distance_between_origin:
                the(p1.square_dist()).should.equal(p1.x * p1.x + p1.y * p1.y)

        with provided.the_other_point_is_given:
            dx, dy = p1.x - p2.x, p1.y - p2.y

            with then.the_result_is_correctly_calculated:
                the(p1.square_dist(p2)).should.equal(dx * dx + dy * dy)

            with and_.should_be_reflective:
                the(p2.square_dist(p1)).should.equal(dx * dx + dy * dy)

    with when.calculate_absolute_value:
        p = Point(3, 4)

        with then.the_result_should_be_correct:
            the(abs(p)).should.equal(5)
