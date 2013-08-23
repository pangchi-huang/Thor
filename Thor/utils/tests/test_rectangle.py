#!/usr/bin/env python

# standard library imports
import random

# third party related imports
from pyspecs import and_, given, provided, the, then, this, when

# local library imports
from Thor.utils.Rectangle import Point, Rectangle


with given.a_rectangle:

    r = Rectangle(0, 0, 4, 3)

    with then.can_calculate_its_area_correctly:
        the(r.area).should.equal(4 * 3)

    with then.its_vertices_can_be_correctly_enumerated:
        vertices = r.vertices

        the(vertices[0]).should.equal(Point(0, 0))
        the(vertices[1]).should.equal(Point(4, 0))
        the(vertices[2]).should.equal(Point(4, 3))
        the(vertices[3]).should.equal(Point(0, 3))


with given.two_rectangles:

    with when.find_intersection_of_these_two_rectangles:

        with provided.they_share_an_edge:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(5, 0, 10, 10)

            with then.it_is_not_considered_intersect:
                the(r1 & r2).should.be(None)

        with provided.they_are_really_disjoint:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(0, 10, 10, 10)

            with then.the_intersection_result_is_None:
                the(r1 & r2).should.be(None)

        with provided.one_contains_the_other:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(1, 1, 2, 2)

            with then.the_intersection_is_the_containee:
                r = r1 & r2
                the(r.x).should.equal(1)
                the(r.y).should.equal(1)
                the(r.w).should.equal(2)
                the(r.h).should.equal(2)

        with provided.they_are_overlapping:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(3, 3, 10, 10)

            with then.the_intersection_should_be_correct:
                r = r1 & r2
                the(r.x).should.equal(3)
                the(r.y).should.equal(3)
                the(r.w).should.equal(2)
                the(r.h).should.equal(2)

    with when.find_union_of_these_two_rectangles:

        with provided.one_contains_the_other:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(1, 1, 2, 2)

            with then.the_union_is_the_container:
                r = r1 | r2
                the(r).should.equal(r1)

        with provided.they_are_overlapping:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(3, 3, 10, 10)

            with then.the_result_should_be_correct:
                r = r1 | r2
                the(r).should.equal(Rectangle(0, 0, 13, 13))

        with provided.they_are_not_overlapping:
            r1 = Rectangle(0, 0, 1, 1)
            r2 = Rectangle(1, 1, 3, 3)

            with then.the_result_should_be_correct:
                r = r1 | r2
                the(r).should.equal(Rectangle(0, 0, 4, 4))

    with when.calculate_the_distance_between_them:

        with provided.they_are_overlapping:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(3, 3, 10, 10)

            with then.the_distance_is_0:
                the(r1.distance(r2)).should.equal(0)
                the(r2.distance(r1)).should.equal(0)

        with provided.they_share_an_edge:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(5, 0, 5, 5)

            with then.the_distance_is_0:
                the(r1.distance(r2)).should.equal(0)
                the(r2.distance(r1)).should.equal(0)

        with provided.they_are_not_overlapping:
            r1 = Rectangle(0, 0, 1, 1)
            r2 = Rectangle(5, 4, 100, 1)

            with then.the_result_should_be_correct:
                the(r1.distance(r2)).should.equal(25)
                the(r2.distance(r1)).should.equal(25)

    with when.calculate_the_distance_between_them_after_projecting_on_axis:

        with provided.one_contains_the_other:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(1, 1, 3, 3)

            with then.the_x_norm_is_0:
                the(r1.x_norm(r2)).should.equal(0)
                the(r2.x_norm(r1)).should.equal(0)

            with then.the_y_norm_is_0:
                the(r1.y_norm(r2)).should.equal(0)
                the(r2.y_norm(r1)).should.equal(0)

        with provided.they_are_overlapping_after_projecting_on_x_axis:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(3, 10, 100, 1)

            with then.the_x_norm_is_0:
                the(r1.x_norm(r2)).should.equal(0)
                the(r2.x_norm(r1)).should.equal(0)

        with provided.they_are_overlapping_after_projecting_on_y_axis:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(100, 1, 1, 100)

            with then.the_y_norm_is_0:
                the(r1.y_norm(r2)).should.equal(0)
                the(r2.y_norm(r1)).should.equal(0)

        with provided.they_are_not_overlapping_after_projecting_on_x_axis:
            r1 = Rectangle(0, 0, 5, 5)
            r2 = Rectangle(10, 10, 20, 5)

            with then.the_x_norm_should_be_correct:
                the(r1.x_norm(r2)).should.equal(5)
                the(r2.x_norm(r1)).should.equal(5)

            with then.the_y_norm_should_be_correct:
                the(r1.y_norm(r2)).should.equal(5)
                the(r2.y_norm(r1)).should.equal(5)
