#!/usr/bin/env python

# standard library imports
import os.path

# third party related imports
from pyspecs import given, it, the, when

# local library imports
from Thor.pdf.page import PDFPage


curr_dir = os.path.dirname(os.path.abspath(__file__))

with given.a_pdf:

    sample_pdf = os.path.join(curr_dir, 'sample', 'test1.pdf')

    with when.parse_page_bounding_box:
        media_box = (0, 0, 683.15, 853.23)
        crop_box = (36.85, 36.85, 646.30, 816.38)
        bleed_box = (36.85, 36.85, 646.30, 816.38)
        trim_box = (36.85, 36.85, 646.30, 816.38)
        art_box = (36.85, 36.85, 646.30, 816.38)

        bboxes = PDFPage.get_page_bbox(sample_pdf)

        def bboxes_almost_the_same(bbox1, bbox2):
            for i in xrange(4):
                the(abs(bbox1[i] - bbox2[i])).should.be_less_than(1.0e-3)

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
