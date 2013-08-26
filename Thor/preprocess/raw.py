#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from Thor.pdf.page import PDFPage


__all__ = ['RawTextPreprocessor']


class RawTextPreprocessorException(Exception): pass


class RawTextPreprocessor(object):
    """Preprocessor which helps to reconstruct words to line segment.

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

    def _merge(self, raw_stream_ix):

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

    def run(self):
        return


class Word(object):
    """A data structure for word object.

    Attributes:
        matches: A list of Match instances.

    """

    def __init__(self, word_obj):

        self._word_obj = word_obj
        self.matches = []

    def __getitem__(self, attr):

        return self._word_obj[attr]


class Stream(object):
    """A data structure for raw stream object.

    Attributes:
        matches: A list of Match instances.

    """

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

        if len(self.matches) == 0:
            return False

        counter = [0] * len(self._stream)

        for match in self.matches:
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

        self._may_merge = ret

        return ret


class Match(object):
    """A data structure for match information of raw stream and word."""

    def __init__(self, index, data, start, end):

        self.index = index
        self.data = data
        self.start = start
        self.end = end
