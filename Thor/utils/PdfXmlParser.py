#!/usr/bin/env python

# standard library imports
from contextlib import closing
from HTMLParser import HTMLParser
import json
import re
import sys

# third party related imports

# local libary imports


__all__ = ['PDFXMLParser', 'PageError', 'WordError']


class WordError(Exception): pass


class Word(object):
    """A data structure representing a word object.

    Attributes:
        x_min: The minimum x of the word.
        y_min: The minimum y of the word.
        x_max: The maximum x of the word.
        y_max: The maximum y of the word.
        text: The text content of the word.
        line: The xml string containing the word.

    """

    html_parser = HTMLParser()

    def __init__(self, lines, line_ix):

        self.x_min = self.y_min = self.x_max = self.y_max = 0
        self.text = None
        self.lines = lines
        self.line_ix = line_ix

    def run(self):
        """Parse word attributes and text from xml."""

        self._expect_correct_marker()

        lines, line_ix = [], self.line_ix
        line = self.lines[line_ix].rstrip()
        while not line.endswith('</word>'):
            lines.append(line)
            line_ix += 1
            line = self.lines[line_ix].rstrip()
        else:
            lines.append(line)
            line_ix += 1

        line = '\n'.join(lines).strip()
        ix = line.find('>')
        if ix == -1:
            raise WordError('Not a valid beginning tag for word object')

        # between '>' and '</word>'
        self.text = self.html_parser.unescape(line[ix + 1:-7])
        self._extract_word_attributes(line[5:ix])

        return line_ix

    @property
    def __json__(self):
        """A dict representing the word."""

        return {
            'x': self.x_min,
            'y': self.y_min,
            'w': self.x_max - self.x_min,
            'h': self.y_max - self.y_min,
            't': self.text or ' '
        }

    def _expect_correct_marker(self):

        line = self.lines[self.line_ix].strip()
        if not line.startswith('<word'):
            raise WordError('Not a valid word markup')

    def _extract_word_attributes(self, line):

        is_x_min_extracted = is_y_min_extracted = False
        is_x_max_extracted = is_y_max_extracted = False
        parts = line.split(' ')

        for part in parts:
            if part.startswith('xMin='):
                self.x_min = float(part[6:-1])
                is_x_min_extracted = True
            elif part.startswith('xMax='):
                self.x_max = float(part[6:-1])
                is_x_max_extracted = True
            elif part.startswith('yMin='):
                self.y_min = float(part[6:-1])
                is_y_min_extracted = True
            elif part.startswith('yMax='):
                self.y_max = float(part[6:-1])
                is_y_max_extracted = True

        if not (is_x_min_extracted and is_x_max_extracted and \
                is_y_max_extracted and is_y_max_extracted):
            raise WordError('Do not extract word geometry information')


class PageError(Exception): pass


class Page(object):
    """A data structure representing a page.

    Attributes:
        width: A float that is the page's width.
        height: A float that is the page's height.
        page_num: An int that is the page number.
        xml_lines: A list of xml string splited by newline.
        line_ix: An int that is the index of xml_lines.

    """

    def __init__(self, page_num, xml_lines, line_ix):
        self.width = self.height = 0
        self.words = []
        self.page_num = page_num
        self.xml_lines = xml_lines
        self.line_ix = line_ix

    def run(self):
        """Parse page object from xml.

        Returns:
            An int that is the index of xml_lines of next page object.

        """

        line = self.xml_lines[self.line_ix].strip()

        self._expect_correct_marker(line)
        self._extract_width_height(line)
        self.line_ix += 1

        while self.line_ix < len(self.xml_lines):
            line = self.xml_lines[self.line_ix].strip()
            if line == '</page>':
                return self.line_ix + 1

            self.line_ix = self._extract_word()

        raise PageError('Do not find </page>')

    @property
    def __json__(self):
        """A dict representing the page."""

        return {
            'width': self.width,
            'height': self.height,
            'page': self.page_num,
            'data': self.words
        }

    def _expect_correct_marker(self, line):

        if not (line.startswith('<page') and line.endswith('>')):
            raise PageError('Not a beginning tag for page object')

    def _extract_width_height(self, line):

        is_width_extracted = is_height_extracted = False
        # strip the beginning '<' and ending '>'
        parts = line[1:-1].split(' ')
        for part in parts:
            if part.startswith('width='):
                self.width = float(part[7:-1])
                is_width_extracted = True
            elif part.startswith('height='):
                self.height = float(part[8:-1])
                is_height_extracted = True

        if not (is_width_extracted and is_height_extracted):
            raise PageError('Do not have width or height information')

    def _extract_word(self):

        word = Word(self.xml_lines, self.line_ix)
        self.line_ix = word.run()
        self.words.append(word.__json__)

        return self.line_ix


class PDFXMLParser(object):
    """A XML parser to parse the xml output of `pdftotext -bbox`

    Attributes:
        xml_lines: A list of string splited by newline.
        pages: A list of dict.
        line_ix: The index of xml_lines.

    """

    def __init__(self, xml_string):
        self.xml_lines = self._find_enclosing_doc_marker(xml_string)\
                             .split('\n')
        self.pages = []
        self.line_ix = 0

    def run(self):
        """Parse xml.

        Returns:
            A list of page dict.

        """

        page_num = 1

        while self.line_ix < len(self.xml_lines):
            line = self.xml_lines[self.line_ix].strip()
            if line.startswith('<page'):
                page = Page(page_num, self.xml_lines, self.line_ix)
                self.line_ix = page.run()
                self.pages.append(page.__json__)
                page_num += 1
            else:
                self.line_ix += 1

        return self.pages

    def _find_enclosing_doc_marker(self, xml_string):

        start = xml_string.find('<doc>')
        end = xml_string.rfind('</doc>') + 6
        return xml_string[start:end]


def main(argv):

    if len(argv) != 2:
        print 'usage: python %s xml-file' % argv[1]
        exit(1)

    with closing(open(argv[1], 'rb')) as f:
        data = f.read().decode('utf8')

    parsed = PDFXMLParser(data).run()

    print json.dumps(parsed, ensure_ascii=False, indent=4).encode('utf8')


if __name__ == '__main__':

    main(sys.argv)
