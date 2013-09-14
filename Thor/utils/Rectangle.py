#!/usr/bin/env python

# standard library imports
from collections import namedtuple
from itertools import product

# third party related imports

# local library imports
from Interval import Interval
from Point import Point


class Rectangle(object):
    """A utility class for rectangle data structure.

    Attributes:
        x: The x-coordinate of the left up corner of this rectangle.
        y: The y-coordinate of the left up corner of this rectangle.
        w: The width of this rectangle.
        h: The height of this rectangle.

    """

    def __init__(self, x, y, w, h):

        self._x = x
        self._y = y
        self._w = w
        self._h = h

    @property
    def x(self):

        return self._x

    @property
    def y(self):

        return self._y

    @property
    def w(self):

        return self._w

    @property
    def h(self):

        return self._h

    def __repr__(self):
        """Get the string representation of this object."""

        return "Rectangle(x=%s, y=%s, w=%s, h=%s)" % (self.x, self.y,
                                                      self.w, self.h)

    @property
    def area(self):
        """Get the area of this rectangle."""

        return self.w * self.h

    @property
    def vertices(self):
        """Four corners of this rectangle.

        Get 4 Point instances from left up corner clockwisely.

        Returns:
            A tuple consists of 4 Point instances.

        """

        return (
            Point(self.x, self.y),
            Point(self.x + self.w, self.y),
            Point(self.x + self.w, self.y + self.h),
            Point(self.x, self.y + self.h),
        )

    def distance(self, other):
        """Distnace between another rectangle.

        The closest distance between my four points to other's four
        points. If two rectangles overlaps, then 0 is returned.

        Args:
            other: A Rectangle instance.

        Returns:
            A number representing the square of L2 norm.

        """

        if self.intersect(other) is not None:
            return 0

        min_dist = float('inf')
        for v1, v2 in product(self.vertices, other.vertices):
            d = v1.square_dist(v2)
            if d < min_dist:
                min_dist = d

        return min_dist

    def intersect(self, other):
        """Get the intersection area of two rectangles.

        Args:
            other: A Rectangle instance.

        Returns:
            If two rectangles overlaps then the intersection area is
            returned. Otherwise, None is returned.

        """

        r1, r2 = self, other

        x_intersect = Interval(r1.x, r1.x + r1.w) & Interval(r2.x, r2.x + r2.w)
        if x_intersect is None:
            return None

        y_intersect = Interval(r1.y, r1.y + r1.h) & Interval(r2.y, r2.y + r2.h)
        if y_intersect is None:
            return None

        return Rectangle(x_intersect.begin, y_intersect.begin,
                         x_intersect.length, y_intersect.length)


    def __and__(self, other):
        """Implements & operator."""

        return self.intersect(other)

    def __iand__(self, other):
        """Implements &= operator."""

        result = self.intersect(other)

        if result is not None:
            self._x, self._y = result.x, result.y
            self._w, self._h = result.w, result.h
            return self

        return None

    def union(self, other):
        """Get the union of two rectangles.

        Args:
            other: A Rectangle instance.

        Returns:
            A Rectangle instance.

        """

        min_x = min(self.x, other.x)
        min_y = min(self.y, other.y)
        max_x = max(self.x + self.w, other.x + other.w)
        max_y = max(self.y + self.h, other.y + other.h)

        return Rectangle(min_x, min_y, max_x - min_x, max_y - min_y)

    def __or__(self, other):
        """Implements | operator."""

        return self.union(other)

    def __ior__(self, other):
        """Implements |= operator."""

        result = self.union(other)

        self._x, self._y = result.x, result.y
        self._w, self._h = result.w, result.h

        return self

    def __eq__(self, other):
        """Implements == operator."""

        return self.x == other.x and self.y == other.y and \
               self.w == other.w and self.h == other.h

    def __hash__(self):
        """Use Rectangle as dict key."""

        return hash((self.x, self.y, self.w, self.h))

    def x_norm(self, other):
        """The distance between rectangles projected on x-axis."""

        line1 = (self.x, self.x + self.w)
        line2 = (other.x, other.x + other.w)

        if line1[1] < line2[0]:
            return line2[0] - line1[1]
        elif line1[0] > line2[1]:
            return line1[0] - line2[1]

        return 0

    def y_norm(self, other):
        """The distance between rectangles projected on y-axis."""

        line1 = (self.y, self.y + self.h)
        line2 = (other.y, other.y + other.h)

        if line1[1] < line2[0]:
            return line2[0] - line1[1]
        elif line1[0] > line2[1]:
            return line1[0] - line2[1]

        return 0


class TextRectangle(Rectangle):
    """A utility data structure for bounding box containing text.

    Attributes:
        t: The text in the bounding box.

    """

    UNKNOWN = 0
    LANDSCAPE = 1
    PORTRAIT = 2

    def __init__(self, x, y, w, h, t):

        super(TextRectangle, self).__init__(x, y, w, h)
        self._t = t
        self._orientation = None

    @classmethod
    def create(cls, word_obj):

        return cls(word_obj['x'], word_obj['y'],
                   word_obj['w'], word_obj['h'], word_obj['t'])

    @property
    def t(self):

        return self._t

    @property
    def orientation(self):
        """Represents the text reading direction."""

        if self._orientation is not None:
            return self._orientation

        if self.t is None:
            self._orientation = self.UNKNOWN
        elif len(self.t) > 1:
            if self.w == self.h:
                self._orientation = self.UNKNOWN
            elif self.w > self.h:
                self._orientation = self.LANDSCAPE
            else:
                self._orientation = self.PORTRAIT
        else:
            self._orientation = self.UNKNOWN

        return self._orientation

    def __repr__(self):
        """Get the string representation of this object."""

        return "TextRectangle(x={x}, y={y}, w={w}, h={h}, t={t})".\
               format(self.__dict__)

    def __eq__(self, other):
        """Implements == operator."""

        return self.x == other.x and self.y == other.y and \
               self.w == other.w and self.h == other.h and \
               self.t == other.t

    def __hash__(self):
        """Use TextRectangle as dict key."""

        return hash((self.x, self.y, self.w, self.h, self.t))