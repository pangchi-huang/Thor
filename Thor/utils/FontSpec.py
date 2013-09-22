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