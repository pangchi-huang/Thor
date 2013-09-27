#!/usr/bin/env python

# standard library imports
from itertools import combinations, permutations

# third party related imports

# local library imports
from Thor.pdf.page import PDFPage
from Thor.utils.Point import Point
from Thor.utils.Rectangle import Rectangle


__all__ = ['RawTextPreprocessor', 'RawTextPreprocessorException']


class RawTextPreprocessorException(Exception): pass


class RawTextPreprocessor(object):
    """Preprocessor which helps to reconstruct words to line segment.

    The preprocessor extracts raw content stream from pdf and
    reconstructs words to line segment by taking advantage of raw
    content stream.

    Attributes:
        page: A PDFPage instance.
        raw_streams: A list of Stream instance.
        words: A list of Word instance.

    """

    def __init__(self, pdf_filename, page):

        self.page = page
        self.words = map(Word, page.words)
        self.raw_streams = map(Stream, page.extract_raw_texts(pdf_filename,
                                                              page.page_num))
        self._associate_word_with_stream()

    def _associate_word_with_stream(self):

        for word_ix, word in enumerate(self.words):
            for stream_ix, stream in enumerate(self.raw_streams):
                for start in stream.find_word(word):
                    end = start + len(word['t'])

                    word_match = Match(stream_ix, stream, start, end)
                    word.matches.append(word_match)

                    stream_match = Match(word_ix, word, start, end)
                    stream.matches.append(stream_match)

    def _merge_words_of_stream(self, raw_stream_ix):

        raw_stream = self.raw_streams[raw_stream_ix]
        if not raw_stream.may_merge():
            raise RawTextPreprocessorException("can't merge")

        word_indices = map(lambda m: m.index, raw_stream.matches)
        for word_ix in word_indices:
            self.words[word_ix].matches = filter(
                lambda m: m.index == raw_stream_ix,
                self.words[word_ix].matches
            )

            for stream_ix in xrange(len(self.raw_streams)):
                if stream_ix == raw_stream_ix:
                    continue

                self.raw_streams[stream_ix].matches = filter(
                    lambda m: m.index != word_ix,
                    self.raw_streams[stream_ix].matches
                )

        union = self.words[word_indices[0]].rectangle
        for word_ix in word_indices:
            union |= self.words[word_ix].rectangle

        return {
            'x': union.x, 'y': union.y,
            'w': union.w, 'h': union.h,
            't': raw_stream._stream,
        }

    def run(self):
        """Main function.

        Merging words by taking advantage of raw stream content.
        Reducing number of words of a PDFPage.

        Returns:
            A PDFPage instance.

        """

        ret = PDFPage(page_num=self.page.page_num,
                      width=self.page.width,
                      height=self.page.height,
                      words=[])

        can_merge_streams = set()
        keep_merging = True
        while keep_merging:
            keep_merging = False

            # the more lengthy words merge earlier
            sorted_streams = sorted(
                zip(xrange(len(self.raw_streams)), self.raw_streams),
                key=lambda (s_ix, s): -1 * len(s._stream)
            )
            for stream_ix, stream in sorted_streams:
                if stream_ix not in can_merge_streams:
                    if not stream.may_merge():
                        num_matches = len(stream.matches)
                        stream.discard_outliers()

                    if stream.may_merge():
                        can_merge_streams.add(stream_ix)
                        ret.words.append(self._merge_words_of_stream(stream_ix))
                        keep_merging = True


        flags = [True] * len(self.words)
        for stream_ix in can_merge_streams:
            stream = self.raw_streams[stream_ix]
            for match in stream.matches:
                flags[match.index] = False

        for word_ix, word in enumerate(self.words):
            if flags[word_ix]:
                ret.words.append(word._word_obj)

        return ret


class Word(object):
    """A data structure for word object.

    Attributes:
        matches: A list of Match instances.
        rectangle: A Rectangle instance of the word's bounding box.

    """

    def __init__(self, word_obj):

        self._word_obj = word_obj
        self.matches = []

    def __getitem__(self, attr):

        return self._word_obj[attr]

    @property
    def rectangle(self):
        """A Rectangle instance of the word's bounding box."""

        return Rectangle(self['x'], self['y'], self['w'], self['h'])

    def __repr__(self):

        return 'Word<_word_obj=%s>' % self._word_obj

class Stream(object):
    """A data structure for raw stream object.

    Attributes:
        matches: A list of Match instances.

    """

    discard_cache = {}

    def __init__(self, stream):

        self._stream = stream
        self._may_merge = False
        self.matches = []

    def find_word(self, word):
        """Locate all the substrings composed of word.

        Args:
            word: An instance of Word.

        Returns:
            A list of string indices.

        """

        ret = []
        start_pos, stream_size = 0, len(self._stream)

        while start_pos < stream_size:
            if word['t'] is None:
                print word.__dict__
            ix = self._stream.find(word['t'], start_pos)
            if ix == -1:
                break

            ret.append(ix)
            start_pos = ix + 1

        return ret

    def may_merge(self):
        """Test whether or not the stream's matching words can be merged.

        The matching words should not overlap and can only be separated
        by spaces.

        Returns:
            A bool.

        """

        if self._may_merge:
            return True

        self._may_merge = self._may_reconstruct_by(self.matches)

        return self._may_merge

    def _may_reconstruct_by(self, matches):

        if len(matches) == 0:
            return False

        counter = [0] * len(self._stream)

        for match in matches:
            for ix in xrange(match.start, match.end):
                counter[ix] += 1

        ret = True
        for ix in xrange(len(self._stream)):
            if counter[ix] > 1:
                ret = False
                break
            elif counter[ix] == 0 and self._stream[ix] != ' ':
                ret = False
                break

        return ret

    def discard_outliers(self):
        """Try to discard words that would not fit to a horizontal line.

        Returns:
            A bool.

        """

        cache_key = '[%s][%s]' % \
                    (self._stream,
                     ','.join(map(lambda m: str(m.index), self.matches)))
        if cache_key in Stream.discard_cache:
            return Stream.discard_cache[cache_key]

        num_matches = len(self.matches)

        # too many matches will spend a lot of computing time
        if num_matches < 3 or num_matches > 30:
            Stream.discard_cache[cache_key] = False
            return False

        centroids = map(
            lambda m: Point(m.data['x'] + m.data['w'] / 2,
                            m.data['y'] + m.data['h'] / 2),
            self.matches
        )

        best_cost = float('inf')
        best_matches = None

        for match_indices in self._enumerate_word_combinations():
            if len(match_indices) <= 1:
                continue

            if self._has_duplicate_word(match_indices):
                continue

            match_set = map(lambda mix: self.matches[mix], match_indices)
            if  sorted(match_set, key=lambda m: m.start) != \
                sorted(match_set, key=lambda m: m.data['x']):
                continue

            # simple linear regression
            points = map(lambda ix: centroids[ix], match_indices)
            a, b = _get_linear_regression_params(points)
            x_variance = _get_std_deviation(map(lambda p: p.x, points))
            # just in case slope is 0
            cost = (abs(a) + 1.0e-6) * x_variance

            if cost < best_cost:
                best_cost = cost
                best_matches = match_indices

        if best_matches is None:
            Stream.discard_cache[cache_key] = False
            return False

        self.matches = map(lambda i: self.matches[i], best_matches)
        Stream.discard_cache[cache_key] = True

        return True

    def _enumerate_word_combinations(self):

        ret = []
        self._target_mask = map(lambda ch: 0 if ch == ' ' else 1, self._stream)

        for match_ix in xrange(len(self.matches)):
            mask = [0] * len(self._target_mask)
            match = self.matches[match_ix]
            for i in xrange(match.start, match.end):
                mask[i] = 1

            self._recursive_find_combination([match_ix], mask,
                                             match_ix + 1, ret)

        return ret

    def _recursive_find_combination(self, curr_match_ixs, curr_mask,
                                    next_match_ix, result):

        if self._target_mask == curr_mask:
            result.append(curr_match_ixs)
            return

        for match_ix in xrange(next_match_ix, len(self.matches)):
            maybe_match = self.matches[match_ix]
            mask = curr_mask[:]
            maybe = True

            for i in xrange(maybe_match.start, maybe_match.end):
                if mask[i] != 0:
                    maybe = False
                    break

                mask[i] = 1

            if maybe:
                self._recursive_find_combination(
                    curr_match_ixs[:] + [match_ix],
                    mask, match_ix + 1, result
                )

    def _has_duplicate_word(self, match_indices):

        word_indices = map(lambda i: self.matches[i].index, match_indices)
        word_set = {wix: True for wix in word_indices}
        return len(word_set) != len(match_indices)


class Match(object):
    """A data structure for match information of raw stream and word."""

    def __init__(self, index, data, start, end):

        self.index = index
        self.data = data
        self.start = start
        self.end = end

    def __repr__(self):

        return 'Match<index=%s, data=%s, start=%s, end=%s>' % \
               (self.index, self.data, self.start, self.end)


def _get_linear_regression_params(points):

    num_points = len(points)
    mean = Point(
        sum(map(lambda c: c.x, points)) / num_points,
        sum(map(lambda c: c.y, points)) / num_points
    )

    denominator = sum(map(lambda c: (c.x - mean.x) ** 2, points))
    if denominator == 0:
        return float('inf'), None

    a = sum(map(lambda c: (c.x - mean.x) * (c.y - mean.y), points)) / \
        denominator
    b = mean.y - a * mean.x

    return a, b


def _get_std_deviation(data):

    sorted_data = sorted(data)
    count = len(data)
    avg = 1. * sum(data) / count
    return 1. * (sum((d * d for d in data)) - count * avg * avg) / count