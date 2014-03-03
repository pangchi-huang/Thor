#!/usr/bin/env

# standard library imports
import string

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
        """Implements member test of TextRectangle."""

        return word in self.words

    @property
    def reading_direction(self):
        """Get reading direction of words inside this space.

        Returns:
            Either LEFT_TO_RIGHT or TOP_TO_BOTTOM.

        Raises:
            DocumentSpaceException: An error occurred if there is no
            word inside.

        """

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

        elif self.word_stat.horizontal_word_count > \
             self.word_stat.vertical_word_count:
            self._reading_direction = self.LEFT_TO_RIGHT

        else:
            self._reading_direction = self.TOP_TO_BOTTOM

        return self._reading_direction

    def enumerate_vertical_cuts(self, min_size=0, scale=1., offset=0.):
        """Enumerates all vertical cuts.

        Args:
            min_size: Minimum width of vertical cut. All enumerated
                vertical cuts must have width greater than it.
            scale: A floating number to scale each word against its
                center.
            offset: A floating number to translate each word.

        Returns:
            A list of Rectangle instances.

        """

        ret = []
        world = [float('inf'), float('inf'), -float('inf'), -float('inf')]
        intervals = IntervalList()

        for word in self.words:
            if word.x < world[0]:
                world[0] = word.x
            if word.x + word.w > world[2]:
                world[2] = word.x + word.w

            if word.y < world[1]:
                world[1] = word.y
            if word.y + word.h > world[3]:
                world[3] = word.y + word.h

            i = Interval(word.x, word.x + word.w)

            if scale != 1.:
                begin, end = i.begin, i.end
                i.begin = (begin * (1 + scale) + end * (1 - scale)) * 0.5
                i.end = (begin * (1 - scale) + end * (1 + scale)) * 0.5

            i.begin += offset
            i.end += offset
            intervals.add(i)

        for c in intervals.gaps:
            if c.length < min_size:
                continue

            cut = Rectangle(c.begin, world[1], c.length, world[3] - world[1])
            ret.append(cut)

        return ret

    def get_widest_vertical_cut(self, min_size=0, scale=1., offset=0.):
        """Get the biggest vertical cut.

        Args:
            min_size: The returned vertical width must have width
                greater than it.
            scale: A floating number to scale each word against its
                center.
            offset: A floating number to translate each word.

        Returns:
            A Rectangle instance. If no vertical cut is available, None
            is returned.

        """

        cuts = self.enumerate_vertical_cuts(min_size, scale, offset)
        if len(cuts) == 0:
            return None
        elif len(cuts) == 1:
            return cuts[0]

        return max(*cuts, key=lambda c: c.w)

    def enumerate_horizontal_cuts(self, min_size=0, scale=1., offset=0.):
        """Enumerates all horizontal cuts.

        Args:
            min_size: Minimum height of horizontal cut. All enumerated
                horizontal cuts must have height greater than it.
            scale: A floating number to scale each word against its
                center.
            offset: A floating number to translate each word.

        Returns:
            A list of Rectangle instances.

        """

        ret = []
        world = [float('inf'), float('inf'), -float('inf'), -float('inf')]
        intervals = IntervalList()

        for word in self.words:
            if word.x < world[0]:
                world[0] = word.x
            if word.x + word.w > world[2]:
                world[2] = word.x + word.w

            if word.y < world[1]:
                world[1] = word.y
            if word.y + word.h > world[3]:
                world[3] = word.y + word.h

            i = Interval(word.y, word.y + word.h)

            if scale != 1.:
                begin, end = i.begin, i.end
                i.begin = (begin * (1 + scale) + end * (1 - scale)) * 0.5
                i.end = (begin * (1 - scale) + end * (1 + scale)) * 0.5

            i.begin += offset
            i.end += offset
            intervals.add(i)

        for c in intervals.gaps:
            if c.length < min_size:
                continue

            cut = Rectangle(world[0], c.begin, world[2] - world[0], c.length)
            ret.append(cut)

        return ret

    def get_widest_horizontal_cut(self, min_size=0, scale=1., offset=0.):
        """Get the biggest horizontal cut.

        Args:
            min_size: The returned horizontal width must have height
                greater than it.
            scale: A floating number to scale each word against its
                center.
            offset: A floating number to translate each word.

        Returns:
            A Rectangle instance. If no horizontal cut is available, None
            is returned.

        """

        cuts = self.enumerate_horizontal_cuts(min_size, scale, offset)
        if len(cuts) == 0:
            return None
        elif len(cuts) == 1:
            return cuts[0]

        return max(*cuts, key=lambda c: c.h)

    def cut_vertically(self, cut_point, left_first=True):
        """Cut the space vertically into 2 subspaces.

        Args:
            cut_point: The x coordinate to split.
            left_first: If True, then left subspace will be traversed
                first. Otherwise, the right one first.

        Raises:
            DocumentSpaceException: If any word is cut.

        """

        left, right = [], []

        for word in self.words:
            word_center = word.x + word.w / 2
            if word_center > cut_point:
                right.append(word)
            elif word_center < cut_point:
                left.append(word)
            else:
                raise DocumentSpaceException('cut a word: ' + unicode(word))

        if left_first:
            self.subspaces = (DocumentSpace(left), DocumentSpace(right))
        else:
            self.subspaces = (DocumentSpace(right), DocumentSpace(left))

    def cut_horizontally(self, cut_point, up_first=True):
        """Cut the space horizontally into 2 subspaces.

        Args:
            cut_point: The y coordinate to split.
            up_first: If True, then upper subspace will be traversed
                first. Otherwise, the downside one first.

        Raises:
            DocumentSpaceException: If any word is cut.

        """

        up, down = [], []

        for word in self.words:
            word_center = word.y + word.h / 2
            if word_center > cut_point:
                down.append(word)
            elif word_center < cut_point:
                up.append(word)
            else:
                raise DocumentSpaceException('cut a word: ' + unicode(word))

        if up_first:
            self.subspaces = (DocumentSpace(up), DocumentSpace(down))
        else:
            self.subspaces = (DocumentSpace(down), DocumentSpace(up))

    def segment_words_horizontally(self, min_size=0, scale=1., offset=0.):
        """Segment words by y-coordinate.

        Args:
            min_size: The minimum distance between word segments.
            scale: A floating number to scale each word against its
                center.
            offset: A floating number to translate each word.

        Returns:
            A list of word segments. A word segment is a list of
            TextRectangle instances. For instance,

            [
                [TextRectangle, TextRectangle, ...], # Segment
                [TextRectangle, TextRectangle, ...], # Segment
                ...
            ]

            The returned segments will be returned from top to bottom.

        """

        cuts = self.enumerate_horizontal_cuts(min_size, scale, offset)

        if len(cuts) == 0:
            return [self.words]

        ret = []
        cuts = [0] + map(lambda c: c.y + c.h / 2, cuts) + [float('inf')]
        for i in xrange(len(cuts) - 1):
            y1, y2 = cuts[i], cuts[i + 1]
            cluster = []

            for word in self.words:
                #if y1 <= word.y and word.y + word.h <= y2:
                if y1 <= word.y + word.h / 2 <= y2:
                    cluster.append(word)

            ret.append(cluster)

        return ret

    def segment_words_vertically(self, min_size=0, scale=1., offset=0.):
        """Segment words by x-coordinate.

        Args:
            min_size: The minimum distance between word segments.
            scale: A floating number to scale each word against its
                center.
            offset: A floating number to translate each word.

        Returns:
            A list of word segments. A word segment is a list of
            TextRectangle instances. For instance,

            [
                [TextRectangle, TextRectangle, ...], # Segment
                [TextRectangle, TextRectangle, ...], # Segment
                ...
            ]

            The returned segments will be returned from right to left.

        """

        cuts = self.enumerate_vertical_cuts(min_size, scale, offset)

        if len(cuts) == 0:
            return [self.words]

        ret = []
        cuts = [0] + map(lambda c: c.x + c.w / 2, cuts) + [float('inf')]
        cuts.reverse()
        for i in xrange(len(cuts) - 1):
            x1, x2 = cuts[i], cuts[i + 1]
            cluster = []

            for word in self.words:
                if x2 <= word.x + word.w / 2 <= x1:
                #if x2 <= word.x and word.x + word.w <= x1:
                    cluster.append(word)

            ret.append(cluster)

        return ret

    def extract_words(self):
        """Extracts words inside the space."""

        if len(self.words) == 1:
            return self.words[0].t

        ret = []
        num_char = sum((len(word.t) for word in self.words))

        if self.reading_direction == self.LEFT_TO_RIGHT:
            avg_char_size = 1. * sum((word.w for word in self.words)) / num_char
            segments = self.segment_words_horizontally(scale=0.5)
            map(lambda segment: segment.sort(key=lambda word: word.x), segments)
            median_x = _median(map(lambda segment: segment[0].x, segments))

            prev_fontspec = None
            for segment in segments:
                paragraph = self.concat_words(segment)
                if len(paragraph) == 0:
                    continue

                longest_fontspec = max(
                    map(lambda word: (word.w, word.font), segment),
                    key=lambda x: x[0]
                )[1]

                if longest_fontspec != prev_fontspec:
                    ret.append('\n' + paragraph)
                    prev_fontspec = longest_fontspec
                elif segment[0].x > median_x + avg_char_size * 0.75:
                    ret.append('\n\n' + paragraph)
                else:
                    if len(ret) > 0 and ret[-1][-1] in string.letters:
                        if paragraph[0][0] in string.letters:
                            ret.append(' ')

                    ret.append(paragraph)

        else:
            avg_char_size = 1. * sum((word.h for word in self.words)) / num_char
            segments = self.segment_words_vertically(scale=0.5)
            map(lambda segment: segment.sort(key=lambda word: word.y), segments)
            median_y = _median(map(lambda segment: segment[0].y, segments))
            #print 'avg_char_size:', avg_char_size
            #print 'median_y:', median_y

            prev_fontspec = None
            for segment in segments:
                #print [word.y for word in segment]
                paragraph = self.concat_words(segment)
                if len(paragraph) == 0:
                    continue

                longest_fontspec = max(
                    map(lambda word: (word.h, word.font), segment),
                    key=lambda x: x[0]
                )[1]

                if longest_fontspec != prev_fontspec:
                    ret.append('\n' + paragraph)
                    prev_fontspec = longest_fontspec
                elif segment[0].y > median_y + avg_char_size * 0.75:
                    ret.append('\n\n' + paragraph)
                else:
                    if len(ret) > 0 and ret[-1][-1] in string.letters:
                        if paragraph[0][0] in string.letters:
                            ret.append(' ')

                    ret.append(paragraph)

        return ''.join(ret)

    def traverse(self, ret=None):

        if self.subspaces is None or len(self.subspaces) == 0:
            ret.append(self.extract_words())
            return

        for subspace in self.subspaces:
            subspace.traverse(ret)

    def concat_words(self, words):

        ret = []

        for word in words:
            if len(word.t) == 0:
                continue

            if len(ret) == 0:
                ret.append(word.t)
                continue

            if ret[-1][-1] in string.letters:
                if word.t[0] in string.letters:
                    ret.append(' ')

            ret.append(word.t)

        return ''.join(ret)


def _median(data):

    sorted_data = sorted(data)

    half = len(sorted_data) / 2
    if len(sorted_data) % 2 == 0:
        return sum(sorted_data[half - 1:half + 1]) / 2.0
    else:
        return sorted_data[half]
