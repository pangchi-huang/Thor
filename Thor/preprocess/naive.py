#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from Thor.pdf.page import PDFPage
from Thor.utils.Point import Point
from Thor.utils.Rectangle import Rectangle


__all__ = []


class NaivePreprocessorException(Exception): pass


class NaivePreprocessor(object):
    """Preprocessor which helps to reconstruct words to line segment.

    The preprocessor merge close words based on some conditions.

    Attributes:
        page: A PDFPage instance.
        words: A list of Word instance.
        factory: An instance of WordFactory.

    """

    def __init__(self, pdf_filename, page,
                 normalize_width=1000,
                 min_dist=3,
                 font_ratio=0.9):

        self.page = page
        self.words = map(Word, page.words)
        self.factory = WordFactory(min_dist, font_ratio)

        self._normalize_width = normalize_width

    def run(self):

        ret = PDFPage(page_num=self.page.page_num,
                      width=self.page.width,
                      height=self.page.height,
                      words=None)

        scale_factor = 1.0 * self._normalize_width / self.page.width
        self._scale_words(scale_factor)

        next_round = []
        while True:
            ismerged = [False] * len(self.words)

            for i, word1 in enumerate(self.words):
                if ismerged[i]:
                    continue

                for j in xrange(i + 1, len(self.words)):
                    if ismerged[j]:
                        continue

                    merged = self.factory.merge(word1, self.words[j])
                    if merged is None:
                        continue

                    ismerged[j] = True
                    word1 = self.words[i] = merged

                next_round.append(word1)

            next_round, self.words = [], next_round

            if not any(ismerged):
                break

        self._scale_words(1.0 / scale_factor)
        ret.words = map(lambda w: w._word_obj, self.words)

        return ret

    def _scale_words(self, scale_factor):

        for word in self.words:
            for attr in 'xywh':
                word._word_obj[attr] *= scale_factor


class Word(object):
    """A data structure for word object.

    Attributes:
        rectangle: A Rectangle instance of the word's bounding box.
        orientation: Must be LANDSCAPE, PORTRAIT, or UNKNOWN

    """

    UNKNOWN = 0
    LANDSCAPE = 1
    PORTRAIT = 2

    def __init__(self, word_obj):

        self._word_obj = word_obj
        self._orientation = None

    def __getitem__(self, attr):

        return self._word_obj[attr]

    @property
    def rectangle(self):
        """A Rectangle instance of the word's bounding box."""

        return Rectangle(self['x'], self['y'], self['w'], self['h'])

    @property
    def orientation(self):
        """Represents the text reading direction."""

        if self._orientation is not None:
            return self._orientation

        if self['t'] is None:
            self._orientation = self.UNKNOWN
        elif len(self['t']) > 1:
            if self['w'] == self['h']:
                self._orientation = self.UNKNOWN
            elif self['w'] > self['h']:
                self._orientation = self.LANDSCAPE
            else:
                self._orientation = self.PORTRAIT
        else:
            self._orientation = self.UNKNOWN

        return self._orientation


class WordFactory(object):
    """A Word instance merger.

    Attributes:
        min_dist: The minimum distance for words to merge together.
        font_ratio: The minimum font size ratio for words to merge together.
        inv_font_ratio: Just 1.0 / font_ratio.

    """

    SIMILARITY = 0.9961946980917455 # cos(5)

    def __init__(self, min_dist, font_ratio):

        self.min_dist = min_dist
        self.font_ratio = font_ratio
        self.inv_font_ratio = 1. / font_ratio

        self.debug = False

    def merge(self, word1, word2):
        """Merge two words into one word.

        Args:
            word1: A Word instance.
            word2: A Word instance.

        Returns:
            If words cannot be merged together, return None. Otherwise,
            a new Word instance is returned.

        """

        o1, o2 = word1.orientation, word2.orientation
        rect1, rect2 = word1.rectangle, word2.rectangle
        dx, dy = rect1.x_norm(rect2), rect1.y_norm(rect2)
        c1 = Point(rect1.x + rect1.w / 2.0, rect1.y + rect1.h / 2.0)
        c2 = Point(rect2.x + rect2.w / 2.0, rect2.y + rect2.h / 2.0)
        w1, w2 = rect1.w, rect2.w
        h1, h2 = rect1.h, rect2.h
        pargs = (o1, o2, dx, dy, c1, c2, w1, w2)
        largs = (o1, o2, dx, dy, c1, c2, h1, h2)


        if o1 == Word.UNKNOWN and o2 == Word.UNKNOWN:
            may_portrait_merge = self._may_merge_in_portrait_direction(*pargs)
            may_landscape_merge = self._may_merge_in_landscape_direction(*largs)

            if may_portrait_merge and may_landscape_merge:
                return self._naive_merge(word1, word2)
            elif may_portrait_merge:
                return self._merge_in_portrait_direction(word1, word2)
            elif may_landscape_merge:
                return self._merge_in_landscape_direction(word1, word2)

            return None

        if o1 == Word.PORTRAIT or o2 == Word.PORTRAIT:
            if self._may_merge_in_portrait_direction(*pargs):
                return self._merge_in_portrait_direction(word1, word2)

        if o1 == Word.LANDSCAPE or o2 == Word.LANDSCAPE:
            if self._may_merge_in_landscape_direction(*largs):
                return self._merge_in_landscape_direction(word1, word2)

        return None

    def _may_merge_in_landscape_direction(self,
                                          orientation1, orientation2,
                                          dx, dy,
                                          center1, center2,
                                          font_size1, font_size2):

        if orientation1 == Word.PORTRAIT or orientation2 == Word.PORTRAIT:
            return False

        if dx > self.min_dist or dy != 0:
            return False

        v = center1 - center2
        cos = abs(v.x) / (v.x * v.x + v.y * v.y) ** 0.5
        if cos < self.SIMILARITY:
            return False

        ratio = 1.0 * font_size1 / font_size2
        if ratio < self.font_ratio or ratio > self.inv_font_ratio:
            return False

        return True

    def _may_merge_in_portrait_direction(self,
                                         orientation1, orientation2,
                                         dx, dy,
                                         center1, center2,
                                         font_size1, font_size2):

        if orientation1 == Word.LANDSCAPE or orientation2 == Word.LANDSCAPE:
            return False

        if dy > self.min_dist or dx != 0:
            return False

        v = center1 - center2
        cos = abs(v.y) / (v.x * v.x + v.y * v.y) ** 0.5
        if cos < self.SIMILARITY:
            return False

        ratio = 1.0 * font_size1 / font_size2
        if ratio < self.font_ratio or ratio > self.inv_font_ratio:
            return False

        return True

    def _merge_in_landscape_direction(self, word1, word2):

        rectangle = word1.rectangle | word2.rectangle
        word_obj = {
            'x': rectangle.x, 'y': rectangle.y,
            'w': rectangle.w, 'h': rectangle.h,
            't': None,
        }

        if word1['x'] <= word2['x']:
            word_obj['t'] = word1['t'] + word2['t']
            #debug = u'"{0}" + "{1}" --> "{0}{1}"'.format(word1['t'], word2['t'])
            #print debug.encode('utf8')
        else:
            word_obj['t'] = word2['t'] + word1['t']
            #debug = u'"{0}" + "{1}" --> "{0}{1}"'.format(word2['t'], word1['t'])
            #print debug.encode('utf8')

        return Word(word_obj)

    def _merge_in_portrait_direction(self, word1, word2):

        rectangle = word1.rectangle | word2.rectangle
        word_obj = {
            'x': rectangle.x, 'y': rectangle.y,
            'w': rectangle.w, 'h': rectangle.h,
            't': None,
        }

        if word1['y'] <= word2['y']:
            word_obj['t'] = word1['t'] + word2['t']
            #debug = u'"{0}" + "{1}" --> "{0}{1}"'.format(word1['t'], word2['t'])
            #print debug.encode('utf8')
        else:
            word_obj['t'] = word2['t'] + word1['t']
            #debug = u'"{0}" + "{1}" --> "{0}{1}"'.format(word2['t'], word1['t'])
            #print debug.encode('utf8')

        return Word(word_obj)

    def _naive_merge(self, word1, word2):

        rectangle = word1.rectangle | word2.rectangle
        word = Word({
            'x': rectangle.x, 'y': rectangle.y,
            'w': rectangle.w, 'h': rectangle.h, 't': None,
        })

        if word.orientation == Word.PORTRAIT:
            return self._merge_in_portrait_direction(word1, word2)

        return self._merge_in_landscape_direction(word1, word2)
