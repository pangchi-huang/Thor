#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports


class FontSpec(object):
    """A data structure for word font information.

    Attributes:
        size: An integer for font size.
        color: A string representing the color, e.g. "221714".

    """

    def __init__(self, size, color):

        self.size = size
        self.color = color

    def __hash__(self):

        return hash((self.size, self.color))

    def __repr__(self):

        return 'FontSpec<size=%s, color=#%s>' % (self.size, self.color)

    def __eq__(self, other):

        return self.size == other.size and self.color == other.color

    @property
    def serializable(self):
        """A JSON serializable."""

        return {'size': self.size, 'color': self.color}

    @classmethod
    def deserialize(cls, serialized):

        if serialized is None:
            return None

        return FontSpec(size=serialized['size'], color=serialized['color'])