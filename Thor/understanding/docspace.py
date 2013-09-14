#!/usr/bin/env

# standard library imports

# third party related imports

# local library imports
from Thor.pdf.page import PDFPage
from Thor.understanding.stat import WordStatistician
from Thor.utils.Rectangle import Rectangle, TextRectangle
from Thor.utils.Interval import Interval, IntervalList


class DocumentSpaceException(Exception): pass


class DocumentSpace(object):
    """A data structure represents a space containing TextRectangles.

    Attributes:
        words: A list of TextRectangle instances.
        subspaces: A list of subspace of DocumentSpace instances.
        reading_direction: Either LEFT_TO_RIGHT or TOP_TO_BOTTOM.

    """

    LEFT_TO_RIGHT = 0
    TOP_TO_BOTTOM = 1

    def __init__(self, words):
        """Constructor

        Args:
            words: A list of TextRectangle instances.

        """

        self.words = words
        self._reading_direction = None
        self.subspaces = None
        self.word_stat = WordStatistician(words)

    def __contains__(self, word):

        return word in self.words

    @property
    def reading_direction(self):

        if self._reading_direction is not None:
            return self._reading_direction

        if len(self.words) == 0:
            raise DocumentSpaceException('There is no word inside.')

        elif len(self.words) == 1:
            word = self.words[0]
            if word.orientation == word.UNKNOWN:
                raise DocumentSpaceException('Cannot detect reading direction.')
            elif word.orientation == word.LANDSCAPE:
                self._reading_direction = self.LEFT_TO_RIGHT
            else:
                self._reading_direction = self.TOP_TO_BOTTOM

        elif self.word_stat.var_width > self.word_stat.var_height:
            self._reading_direction = self.LEFT_TO_RIGHT

        else:
            self._reading_direction = self.TOP_TO_BOTTOM

        return self._reading_direction

    def enumerate_vertical_cuts(self, min_size=0):

        ret = []
        world = [float('inf'), float('inf'), -float('inf'), -float('inf')]
        intervals = IntervalList()

        for word in self.words:
            if word.x < world[0]:
                world[0] = word.x
            elif word.x + word.w > world[2]:
                world[2] = word.x + word.w

            if word.y < world[1]:
                world[1] = word.y
            elif word.y + word.h > world[3]:
                world[3] = word.y + word.h

            intervals.add(Interval(word.x, word.x + word.w))


        for c in intervals.gaps:
            if c.length < min_size:
                continue

            cut = Rectangle(c.begin, world[1], c.length, world[3] - world[1])
            ret.append(cut)

        return ret

    def get_widest_vertical_cut(self, min_size=0):

        cuts = self.enumerate_vertical_cuts(min_size)
        if len(cuts) == 0:
            return None

        return max(*cuts, key=lambda c: c.w)

    def enumerate_horizontal_cuts(self, min_size=0):

        ret = []
        world = [float('inf'), float('inf'), -float('inf'), -float('inf')]
        intervals = IntervalList()

        for word in self.words:
            if word.x < world[0]:
                world[0] = word.x
            elif word.x + word.w > world[2]:
                world[2] = word.x + word.w

            if word.y < world[1]:
                world[1] = word.y
            elif word.y + word.h > world[3]:
                world[3] = word.y + word.h

            intervals.add(Interval(word.y, word.y + word.h))


        for c in intervals.gaps:
            if c.length < min_size:
                continue

            cut = Rectangle(world[0], c.begin, world[2] - world[0], c.length)
            ret.append(cut)

        return ret

    def get_widest_horizontal_cut(self, min_size=0):

        cuts = self.enumerate_horizontal_cuts(min_size)
        if len(cuts) == 0:
            return None

        return max(*cuts, key=lambda c: c.h)

    def cut_vertically(self, cut_point, left_first=True):

        left, right = [], []

        for word in self.words:
            if word.x >= cut_point:
                right.append(word)
            elif word.x + word.w <= cut_point:
                left.append(word)
            else:
                raise DocumentSpaceException('cut a word: ' + unicode(word))

        if left_first:
            self.subspaces = (DocumentSpace(left), DocumentSpace(right))
        else:
            self.subspaces = (DocumentSpace(right), DocumentSpace(left))

    def cut_horizontally(self, cut_point, up_first=True):

        up, down = [], []

        for word in self.words:
            if word.y >= cut_point:
                down.append(word)
            elif word.y + word.h <= cut_point:
                up.append(word)
            else:
                raise DocumentSpaceException('cut a word: ' + unicode(word))

        if up_first:
            self.subspaces = (DocumentSpace(up), DocumentSpace(down))
        else:
            self.subspaces = (DocumentSpace(down), DocumentSpace(up))

    def segment_words_horizontally(self, min_size=0):

        cuts = self.enumerate_horizontal_cuts(min_size)

        if len(cuts) == 0:
            return self.words

        ret = []
        cuts = [0] + map(lambda c: c.y, cuts) + [float('inf')]
        for i in xrange(len(cuts) - 1):
            y1, y2 = cuts[i], cuts[i + 1]
            cluster = []

            for word in self.words:
                if y1 <= word.y and word.y + word.h <= y2:
                    cluster.append(word)

            ret.append(cluster)

        return ret

    def segment_words_vertically(self, min_size=0):

        cuts = self.enumerate_vertical_cuts(min_size)

        if len(cuts) == 0:
            return self.words

        ret = []
        cuts = [0] + map(lambda c: c.x, cuts) + [float('inf')]
        cuts.reverse()
        for i in xrange(len(cuts) - 1):
            x1, x2 = cuts[i], cuts[i + 1]
            cluster = []

            for word in self.words:
                if x2 <= word.x and word.x + word.w <= x1:
                    cluster.append(word)

            ret.append(cluster)

        return ret