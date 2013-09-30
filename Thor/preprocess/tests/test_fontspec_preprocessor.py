#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard library imports
from contextlib import closing
import os.path

# third party realted imports
from pyspecs import and_, as_well_as, given, it, provided, so, the, then, this, when
import ujson

# local library imports
from Thor.pdf.page import PDFPage
from Thor.pdf.text import PDFText
from Thor.preprocess.fontspec import FontSpecPreprocessor
from Thor.utils.FontSpec import FontSpec


with given.a_FontSpecPreprocessor:

    curr_dir = os.path.abspath(os.path.dirname(__file__))
    sample_pdf = os.path.join(curr_dir, 'fixture', 'chew_people_11.pdf')
    sample_json = os.path.join(curr_dir, 'fixture', 'chew_people_11.json')

    with closing(open(sample_json)) as f:
        pdf_json = f.read().decode('utf8')

    preprocessor = FontSpecPreprocessor(
        sample_pdf, PDFPage.loads(pdf_json)
    )

    with then.it_can_extract_all_font_specs_used_by_a_pdf_page:
        ground_truths = [
            FontSpec(size=6, color="221714"),
            FontSpec(size=5, color="221714"),
            FontSpec(size=38, color="221714"),
            FontSpec(size=27, color="221714"),
            FontSpec(size=8, color="221714"),
            FontSpec(size=4, color="000000"),
        ]
        ground_truths.sort(key=lambda fs: fs.size)

        font_specs = preprocessor.font_specs
        font_specs.sort(key=lambda fs: fs.size)
        the(len(font_specs)).should.equal(len(ground_truths))
        for truth, spec in zip(ground_truths, font_specs):
            the(truth.size).should.equal(spec.size)
            the(truth.color).should.equal(spec.color)


    with then.it_can_figure_out_the_font_spec_of_a_textual_object:
        ground_truths = [
            {
                'top': 772 - 36.85, 'left': 28 - 36.85,
                'width': 4, 'height': 9,
                'text': u'9', 'font': FontSpec(size=6, color="221714")
            },
            {
                'top': 566 - 36.85, 'left': 235 - 36.85,
                'width': 94, 'height': 8,
                'text': u'撰文 I 萬岳乘　攝影 I 萬岳乘',
                'font': FontSpec(size=5, color="221714"),
            },
            {
                'top': 521 - 36.85, 'left': 182 - 36.85,
                'width': 200, 'height': 42,
                'text': u'台中秋虹谷', 'font': FontSpec(size=38, color="221714"),
            },
            {
                'top': 569 - 36.85, 'left': 394 - 36.85,
                'width': 31, 'height': 31,
                'text': u'被', 'font': FontSpec(size=27, color="221714"),
            },
        ]
        default_font = FontSpec(size=8, color="221714")

        words = preprocessor._words
        the(len(words)).should.equal(157)
        for word in words:
            isdefault = True
            for truth in ground_truths:
                if word['text'] == truth['text']:
                    for attr in ('top', 'left', 'width', 'height'):
                        the(word[attr]).should.equal(truth[attr])
                    isdefault = False
                    break

            if isdefault:
                the(word['font'].size).should.equal(default_font.size)
                the(word['font'].color).should.equal(default_font.color)


    with then.it_can_use_geometry_info_to_match_word_object_of_a_pdf_page:
        page = {
            'width': 595.28, 'height': 793.7,
            'page': 1, 'data': [
                {
                    "y": 484.5423, "x": 145.4531,
                    "t": u"台中秋虹谷",
                    "w": 200, "h": 42
                },
                {
                    "y": 529.2758, "x": 357.4816,
                    "t": u"被",
                    "w": 29.15, "h": 29.15
                },
                {
                    "y": 577.1258, "x": 365.9816,
                    "t": u"七期豪宅包圍的一窪谷地，",
                    "w": 10.45, "h": 126.7585
                },
            ]
        }
        preprocessor = FontSpecPreprocessor(
            sample_pdf,
            PDFPage.loads(ujson.dumps(page, ensure_ascii=False))
        )
        preprocessor._words = words = [
            {
                'top': 521 - 36.85, 'left': 182 - 36.85,
                'width': 200, 'height': 42,
                'text': u'台中秋虹谷', 'font': FontSpec(size=38, color="221714"),
            },
            {
                'top': 569 - 36.85, 'left': 394 - 36.85,
                'width': 31, 'height': 31,
                'text': u'被', 'font': FontSpec(size=27, color="221714"),
            },
            {
                'top': 615 - 36.85, 'left': 403 - 36.85,
                'width': 11, 'height': 11,
                'text': u'七', 'font': FontSpec(size=8, color="221714"),
            },
            {
                'top': 721 - 36.85, 'left': 403 - 36.85,
                'width': 11, 'height': 11,
                'text': u'地，', 'font': FontSpec(size=8, color="221714"),
            },
            {
                'top': 772 - 36.85, 'left': 28 - 36.85,
                'width': 4, 'height': 9,
                'text': u'9', 'font': FontSpec(size=6, color="221714"),
            }
        ]

        the(preprocessor.match(words[0])).should.equal(PDFText.create_from_dict(page['data'][0]))
        the(preprocessor.match(words[1])).should.equal(PDFText.create_from_dict(page['data'][1]))
        the(preprocessor.match(words[2])).should.equal(PDFText.create_from_dict(page['data'][2]))
        the(preprocessor.match(words[3])).should.equal(PDFText.create_from_dict(page['data'][2]))
        the(preprocessor.match(words[4])).should.be(None)


    with then.every_word_object_of_a_pdf_page_will_have_its_font_spec:
        page = preprocessor.run()
        the(page.words[0].font).should.equal(FontSpec(38, "221714"))
        the(page.words[1].font).should.equal(FontSpec(27, "221714"))
        the(page.words[2].font).should.equal(FontSpec(8, "221714"))
