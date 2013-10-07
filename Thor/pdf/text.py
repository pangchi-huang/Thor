#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from Thor.utils.FontSpec import FontSpec
from Thor.utils.Rectangle import Rectangle, TextRectangle


class PDFTextException(Exception): pass


class PDFText(object):
    """A data structure for textual object in pdf document.

    Attributes:
        x: The x-coordinate of left-upper bounding box.
        y: The y-coordinate of left-upper bounding box.
        w: The width of bounding box.
        h: The height of bounding box.
        t: The text.
        font: The instance of FontSpec.
        orientation: The text reading direction. See TextRectangle.
        rect: The TextRectangle instance.

    """

    def __init__(self, x, y, w, h, t, font=None):

        self._rect = TextRectangle(x, y, w, h, t)
        self._font = font

    @property
    def x(self):

        return self._rect.x

    @property
    def y(self):

        return self._rect.y

    @property
    def w(self):

        return self._rect.w

    @property
    def h(self):

        return self._rect.h

    @property
    def t(self):

        return self._rect.t

    @property
    def font(self):

        return self._font

    @property
    def orientation(self):

        return self._rect.orientation

    def __repr__(self):
        """The string representation of this object."""

        return 'PDFText<x=%s, y=%s, w=%s, h=%s, t=%s, font=%s>' % \
               (self.x, self.y, self.w, self.h, self.t, self.font)

    def __eq__(self, other):

        return self.x == other.x and self.y == other.y and \
               self.w == other.w and self.h == other.h and \
               self.t == other.t and self.font == other.font

    def __ne__(self, other):

        return not self == other

    def __json__(self):

        return {
            'x': self.x, 'y': self.y,
            'w': self.w, 'h': self.h,
            't': self.t,
            'font': self.font.__json__() if self.font is not None else None,
        }

    @property
    def rect(self):

        return self._rect

    @classmethod
    def create_from_dict(cls, value_dict):
        """Create A PDFText instance from a dict."""

        return cls(x=value_dict['x'], y=value_dict['y'],
                   w=value_dict['w'], h=value_dict['h'],
                   t=value_dict['t'],
                   font=FontSpec.deserialize(value_dict.get('font')))
