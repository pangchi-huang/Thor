#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from Thor.pdf.page import PDFPage


class RawTextPreprocessor(object):
    """Preprocessor which helps to reconstruct words to line segment.

    Attributes:
        page: A PDFPage instance.

    """

    def __init__(self, page):

        self.page = page

    def run(self):
        return