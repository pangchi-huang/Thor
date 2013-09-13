#!/usr/bin/env python

# standard library imports

# third party realted imports

# local library imports


class WordStatistician(object):
    """A simple statistics reporter about words.

    Attributes:
        count: The number of words.
        avg_width: The average of word's width.
        avg_height: The average of word's height.
        var_width: The variance of word's width.
        var_height: The variance of word's height.

    """

    def __init__(self, words):
        self.count = self.avg_width = self.avg_height = 0
        self.var_width = self.var_height = 0
        self._run(words)

    def _run(self, words):

        self.count = len(words)

        for ix, word in enumerate(words):
            self.avg_width += 1.0 * word['w']
            self.var_width += 1.0 * word['w'] * word['w']
            self.avg_height += 1.0 * word['h']
            self.var_height += 1.0 * word['h'] * word['h']

        self.avg_width /= self.count
        self.var_width -= self.count * self.avg_width * self.avg_width
        self.var_width /= self.count

        self.avg_height /= self.count
        self.var_height -= self.count * self.avg_height * self.avg_height
        self.var_height /= self.count
