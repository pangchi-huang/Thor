#!/usr/bin/env python

# standard library imports
import os.path

# third party related imports
from pyspecs import and_, given, it, the, then, this, when
import ujson

# local library imports
from Thor.pdf.page import PDFPage
from Thor.utils.Rectangle import Rectangle


curr_dir = os.path.dirname(os.path.abspath(__file__))

with given.a_pdf:

    sample_pdf = os.path.join(curr_dir, 'fixture', 'test1.pdf')

    with when.get_page_bounding_boxes_of_a_page:
        media_box = (0, 0, 683.15, 853.23)
        crop_box = (36.85, 36.85, 646.30, 816.38)
        bleed_box = (36.85, 36.85, 646.30, 816.38)
        trim_box = (36.85, 36.85, 646.30, 816.38)
        art_box = (36.85, 36.85, 646.30, 816.38)

        bboxes = PDFPage.get_page_bboxes(sample_pdf, 1)

        def bboxes_almost_the_same(bbox1, bbox2):
            for i in xrange(4):
                this(abs(bbox1[i] - bbox2[i])).should.be_less_than(1.0e-3)

        with then.media_box_should_be_correct:
            bboxes_almost_the_same(media_box, bboxes['media'])

        with then.crop_box_should_be_correct:
            bboxes_almost_the_same(crop_box, bboxes['crop'])

        with then.bleed_box_should_be_correct:
            bboxes_almost_the_same(bleed_box, bboxes['bleed'])

        with then.trim_box_should_be_correct:
            bboxes_almost_the_same(trim_box, bboxes['trim'])

        with then.art_box_should_be_correct:
            bboxes_almost_the_same(art_box, bboxes['art'])

    sample_pdf = os.path.join(curr_dir, 'fixture', 'test2.pdf')

    with when.extract_texts_from_it:

        with then.default_is_to_extract_from_all_pages:
            pages = PDFPage.extract_texts(sample_pdf)
            the(len(pages)).should.equal(4)
            for ix, page in enumerate(pages):
                the(page.page_num).should.equal(ix + 1)

        with and_.it_can_extract_specified_pages_as_well:
            pages = PDFPage.extract_texts(sample_pdf, (1, 3,))
            the(len(pages)).should.equal(2)
            the(pages[0].page_num).should.equal(1)
            the(pages[1].page_num).should.equal(3)

        with and_.no_word_is_outside_crop_box:
            pages = PDFPage.extract_texts(sample_pdf)
            for page in pages:
                crop_box = Rectangle(0, 0, page.width, page.height)

                for word in page.words:
                    word_box = Rectangle(word['x'], word['y'],
                                         word['w'], word['h'])
                    the(crop_box.intersect(word_box)).should_NOT.be(None)

        with and_.it_can_keep_text_in_content_stream_order:
            for i in xrange(1, 4 + 1):
                raw_textual_objects = PDFPage.extract_raw_texts(sample_pdf, i)
                print raw_textual_objects

    with when.serialize_it_to_json:

        p = PDFPage(page_num=1, width=99.9, height=55.5)
        p.words = [
            {'x': 0, 'y': 0, 'w': 100, 'h': 30, 't': u'GG'},
            {'x': 100, 'y': 250, 'w': 60, 'h': 120, 't': u'drink water'},
        ]
        serialized = PDFPage.dumps(p)
        deserialized = ujson.loads(serialized)

        with then.page_num_should_be_correct:
            the(deserialized['page']).should.equal(1)

        with and_.width_should_be_correct:
            the(abs(deserialized['width'] - 99.9)).should.be_less_than(1.0e-3)

        with and_.height_should_be_correct:
            the(abs(deserialized['height'] - 55.5)).should.be_less_than(1.0e-3)

        with and_.words_should_be_correct:
            for word_ix, word in enumerate(deserialized['data']):
                for key in word:
                    the(word[key]).should.equal(p.words[word_ix][key])

    with when.deserialize_from_json:

        serialized = """
            {
                "page": 2,
                "width": 3.14,
                "height": 1.618,
                "data": [
                    {"x": 3, "y": 0.14, "w": 0.301, "h": 0.4771, "t": "OK"},
                    {"x": 1, "y": 0.618, "w": 0.8451, "h": 0.7781, "t": "FAIL"}
                ]
            }"""
        deserialized = ujson.loads(serialized)
        p = PDFPage.loads(serialized)

        with then.page_num_should_be_correct:
            the(p.page_num).should.equal(2)

        with and_.width_should_be_correct:
            the(abs(p.width - 3.14)).should.be_less_than(1.0e-3)

        with and_.height_should_be_correct:
            the(abs(p.height - 1.618)).should.be_less_than(1.0e-3)

        with and_.words_should_be_correct:
            for word_ix, word in enumerate(deserialized['data']):
                for key in word:
                    the(word[key]).should.equal(p.words[word_ix][key])
