#!/usr/bin/env python

# standard library imports
from collections import Counter, defaultdict
from contextlib import closing
from tempfile import NamedTemporaryFile
import subprocess

# third party related imports
from pyquery import PyQuery

# local library imports
from Thor.pdf.page import PDFPage
from Thor.utils.FontSpec import FontSpec


class FontSpecPreprocessor(object):
    """Preprocessor which gives word its font spec, e.g. color, font size.

    Attributes:
        pdf_filename: The filename of the PDF document.
        page: A PDFPage instance.
        font_specs: A list of FontSpec instances.

    """

    def __init__(self, pdf_filename, page):

        self.pdf_filename = pdf_filename
        self.page = page

        self._fontspecs = {}
        self._words = []

        self.convert_to_xml()

    @property
    def font_specs(self):
        """A list of FontSpec instances."""

        return self._fontspecs.values()

    def match(self, word):
        """Match an xml textual object to a PDFPage word object.

        Currently, the matching process only uses geometry information.
        No textual information is used.

        Args:
            word: An xml textual object.

        Returns:
            A PDFPage word object or None.

        """

        x, y = word['left'], word['top']
        w, h = word['width'], word['height']
        center_x, center_y = x + w / 2., y + h / 2.

        for word in self.page.words:
            if  (word['x'] <= center_x <= word['x'] + word['w']) and \
                (word['y'] <= center_y <= word['y'] + word['h']):
                return word

        return None

    def run(self):
        """Main function.

        Giving FontSpec to word object of PDFPage.

        Returns:
            A PDFPage instance.

        """

        self.page.fonts = self.font_specs

        votes = defaultdict(Counter)
        for word in self._words:
            match_word = self.match(word)
            if match_word is not None:
                votes[id(match_word)][word['font']] += 1

        for match_word_id in votes:
            for word in self.page.words:
                if id(word) == match_word_id:
                    counter = votes[match_word_id]
                    most_fontspec = counter.most_common(1)[0]

                    fontspec_found = False
                    for fontspec in self.page.fonts:
                        if fontspec == most_fontspec[0]:
                            word['font'] = fontspec
                            fontspec_found = True
                            break

                    if fontspec_found:
                        break

        return self.page

    def convert_to_xml(self):
        """
        Call pdftohtml utility to convert pdf to XML for post-
        processing.

        """

        cmd = ('pdftohtml', '-i', '-xml', '-zoom', '1',
               '-f', str(self.page.page_num),
               '-l', str(self.page.page_num),
               '-stdout',
               self.pdf_filename)
        xml = subprocess.check_output(cmd)
        self.parse_xml(xml.decode('utf8'))

    def parse_xml(self, xml_stream):
        """Parse XML and get font spec of every word.

        Args:
            xml_stream: An XML string.

        """

        start = xml_stream.find('<pdf2xml')
        end = xml_stream.find('</pdf2xml>') + 10
        jq = PyQuery(xml_stream[start:end])

        boxes = PDFPage.get_page_bboxes(self.pdf_filename, self.page.page_num)
        crop_box = boxes['crop']

        page_element = jq('page')[0]
        page_width = float(page_element.attrib['width'])
        page_height = float(page_element.attrib['height'])

        fontspec_elements = jq('fontspec')
        for fs in fontspec_elements:
            attr = fs.attrib
            fid, fsize, fcolor = attr['id'], attr['size'], attr['color']
            self._fontspecs[fid] = FontSpec(size=int(fsize), color=fcolor[1:])

        text_elements = jq('text')
        for ix, text in enumerate(text_elements):
            attr = text.attrib
            top, left = float(attr['top']), float(attr['left'])
            width, height = float(attr['width']), float(attr['height'])
            # it is pdftohtml bug
            width = height if width == 0 else width

            if  (top >= page_height or top + height <= 0) or \
                (left + width <= 0 or left > page_width):
                continue

            self._words.append({
                'top': top - crop_box[1], 'left': left - crop_box[0],
                'width': width, 'height': height,
                'text': text.text,
                'font': self._fontspecs[attr['font']],
            })

