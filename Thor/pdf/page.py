#!/usr/bin/env python

# standard library imports
from contextlib import closing
from tempfile import NamedTemporaryFile
import subprocess

# third party related imports
from pyquery import PyQuery
import ujson

# local library imports


__all__ = ['PDFPage']


class PDFPage(object):
    """PDF page

    Attributes:
        page_num: An integer indicating the current page number.
        width: The width of the page
        height: The height of the page
        data: A list of text with bounding box information.

    """

    def __init__(self, page_num=0, width=0, height=0, data=None):

        self.page_num = page_num
        self.width = width
        self.height = height
        self.data = data

    def __json__(self):

        return {
            'page': self.page_num,
            'width': self.width,
            'height': self.height,
            'data': self.data
        }

    def serialize(self):
        """Serialize to JSON"""

        return self.dumps(self)

    @classmethod
    def loads(cls, serialized):
        """Deserialize and convert to a PDFPage instance.

        Args:
            serialized: A string serialized by PDFPage.

        Returns:
            A PDFPage instance.

        """

        deserialized = ujson.loads(serialized)

        ret = PDFPage()
        ret.page_num = deserialized.get('page', 0)
        ret.width = deserialized.get('width', 0)
        ret.height = deserialized.get('height', 0)
        ret.data = deserialized.get('data')

        return ret

    @classmethod
    def dumps(cls, page):
        """Serialize a PDFPage instance to json.

        Args:
            page: A PDFPage instance.

        Returns:
            A JSON string.

        """

        return ujson.dumps(page.__json__(), ensure_ascii=False)

    @classmethod
    def extract_text(cls, filename, pages=None):
        """Create a bunch of PDFPages by xpdf utility program `pdftotext`.

        Args:
            filename: The absolute path of the specified pdf document.
            pages: A list of page numbers to extract. If omitted, all
                pages are extracted.

        Returns:
            A list of PDFPage instances.

        """

        ret = []

        if pages is None:
            with closing(NamedTemporaryFile()) as f:
                cmd = ('pdftotext', '-bbox', filename, f.name)
                subprocess.check_call(cmd)
                parsed_pages = _parse_bboxes(f.name)

            for ix, page_data in enumerate(parsed_pages):
                box_dict = cls.get_page_bbox(filename, ix + 1)
                media_box, crop_box = box_dict['media'], box_dict['crop']
                _transform_to_crop_box_space(page_data, media_box, crop_box)
                ret.append(PDFPage(ix + 1, page_data['width'],
                                   page_data['height'], page_data['data']))

            return ret

        for p in pages:
            with closing(NamedTemporaryFile()) as f:
                cmd = ('pdftotext', '-bbox', '-f', str(p), '-l', str(p),
                       filename, f.name)
                subprocess.check_call(cmd)
                parsed_page = _parse_bboxes(f.name)[0]

            box_dict = cls.get_page_bbox(filename, p)
            media_box, crop_box = box_dict['media'], box_dict['crop']
            _transform_to_crop_box_space(parsed_page, media_box, crop_box)
            ret.append(PDFPage(p, parsed_page['width'],
                               parsed_page['height'], parsed_page['data']))

        return ret

    @classmethod
    def get_page_bbox(cls, filename, page_num):
        """
        Get media box, crop box, bleed box, trim box, art box
        information of the specified PDF page.

        Args:
            filename: The absolute path of the specified pdf document.
            page_num: The number of page. Should be 1-based.

        Returns:
            {
                'media': [0, 0, 683.15, 853.23],
                'crop': [0, 0, 683.15, 853.23],
                'bleed': [0, 0, 683.15, 853.23],
                'trim': [0, 0, 683.15, 853.23],
                'art': [0, 0, 683.15, 853.23]
            }

        """

        pdf_info = subprocess.check_output((
            'pdfinfo', '-box',
            '-f', str(page_num),
            '-l', str(page_num),
            filename
        ))

        ret = {}
        for line in pdf_info.splitlines():
            line = filter(lambda x: x != '', line.split(' '))

            if 'MediaBox:' in line:
                ret['media'] = map(float, line[3:7])
            if 'CropBox:' in line:
                ret['crop'] = map(float, line[3:7])
            if 'BleedBox:' in line:
                ret['bleed'] = map(float, line[3:7])
            if 'TrimBox:' in line:
                ret['trim'] = map(float, line[3:7])
            if 'ArtBox:' in line:
                ret['art'] = map(float, line[3:7])

        return ret


def _parse_bboxes(html):

    with closing(open(html, 'rb')) as f:
        html_txt = f.read().decode('utf8')
        start = html_txt.find('<doc>')
        end = html_txt.find('</doc>') + 6

    pages = []

    jq = PyQuery(html_txt[start:end])
    page_elements = jq('page')
    for i, pg in enumerate(page_elements):
        page_obj = {
            'width': float(pg.attrib['width']),
            'height': float(pg.attrib['height']),
            'page': i + 1,
            'data': [],
        }

        word_elements = pg.findall('word')
        for word in word_elements:
            word_attr = word.attrib
            min_x = float(word_attr.get('xMin') or word_attr['xmin'])
            max_x = float(word_attr.get('xMax') or word_attr['xmax'])
            min_y = float(word_attr.get('yMin') or word_attr['ymin'])
            max_y = float(word_attr.get('yMax') or word_attr['ymax'])
            page_obj['data'].append({
                'x': min_x,
                'y': min_y,
                'w': max_x - min_x,
                'h': max_y - min_y,
                't': word.text,
            })

        pages.append(page_obj)

    return pages

def _transform_to_crop_box_space(data, media_box, crop_box):

    data['width'] = crop_box[2] - crop_box[0]
    data['height'] = crop_box[3] - crop_box[1]

    for txt_obj in data['data']:
        txt_obj['x'] -= crop_box[0]
        txt_obj['y'] -= crop_box[1]