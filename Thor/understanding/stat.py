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
        median_width: The median of word's width.
        median_height: The median of word's height.
        horizontal_word_count: The number of horizontal orientation words.
        vertical_word_count: The number of vertical orientation words.

    """

    def __init__(self, words):
        self.count = self.avg_width = self.avg_height = 0
        self.var_width = self.var_height = 0
        self.horizontal_word_count = self.vertical_word_count = 0
        self._run(words)

    def _run(self, words):

        self.count = len(words)
        if self.count == 0:
            return

        for ix, word in enumerate(words):
            self.avg_width += 1.0 * word.w
            self.var_width += 1.0 * word.w * word.w
            self.avg_height += 1.0 * word.h
            self.var_height += 1.0 * word.h * word.h

            if word.orientation == word.LANDSCAPE:
                self.horizontal_word_count += 1
            elif word.orientation == word.PORTRAIT:
                self.vertical_word_count += 1

        self.avg_width /= self.count
        self.var_width -= self.count * self.avg_width * self.avg_width
        self.var_width /= self.count

        self.avg_height /= self.count
        self.var_height -= self.count * self.avg_height * self.avg_height
        self.var_height /= self.count

        sorted_widths = sorted(map(lambda w: w.w, words))
        sorted_heights = sorted(map(lambda w: w.h, words))
        half = len(words) / 2
        if len(words) % 2 == 0:
            self.median_width = sum(sorted_widths[half - 1:half + 1]) / 2.
            self.median_height = sum(sorted_heights[half - 1:half + 1]) / 2.
        else:
            self.median_width = sorted_widths[half]
            self.median_height = sorted_heights[half]