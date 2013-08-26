#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard library imports
from contextlib import closing
import os.path

# third party related imports
from pyspecs import and_, given, it, provided, so, the, then, this, when
import ujson

# local library imports
from Thor.pdf.page import PDFPage
from Thor.preprocess.raw import RawTextPreprocessor


with given.a_RawTextPreprocessor:

    curr_dir = os.path.abspath(os.path.dirname(__file__))
    sample_json = os.path.join(curr_dir, 'fixture', 'test1.json')
    sample_raw = os.path.join(curr_dir, 'fixture', 'test1.rtxt')
    sample_pdf = os.path.join(curr_dir, 'fixture', 'test1.pdf')

    with closing(open(sample_json)) as f:
        sample = ujson.loads(f.read().decode('utf8'))

    preprocessor = RawTextPreprocessor(PDFPage(page_num=sample['page'],
                                               width=sample['width'],
                                               height=sample['height'],
                                               words=sample['data']))

    with then.it_extracts_texts_in_content_stream_order:

        raw_texts = RawTextPreprocessor.get_raw_texts(sample_pdf, 1)
        with closing(open(sample_raw)) as f:
            expected = f.read().decode('utf8').splitlines()

        the(len(raw_texts)).should.equal(len(expected))
        for ix, raw in enumerate(raw_texts):
            the(raw).should.equal(expected[ix])

    with then.each_word_obj_should_locate_itself_in_every_possible_raw_stream:

        ground_truth = (
            # 0
            (u'時尚雜誌', ((0, 0, 4),)),
            (u'國際中文版', ((1, 0, 5),)),
            (u'2012', ((2, 0, 4),)),
            (u'MAY.', ((2, 5, 9),)),
            (u'五月號', ((3, 0, 3),)),
            # 5
            (u'×', ((8, 0, 1), (21, 0, 1),)),
            (u'iP', ((10, 0, 2),)),
            (u'ad', ((10, 2, 4),)),
            (u'version', ((11, 0, 7),)),
            (u'now', ((11, 8, 11),)),
            # 10
            (u'UE', ((12, 0, 2),)),
            (u'W', ((13, 0, 1), (16, 0, 1),)),
            (u'N', ((4, 3, 4), (14, 0, 1), (17, 0, 1),)),
            (u'M', ((2, 5, 6), (15, 0, 1),)),
            (u'W', ((13, 0, 1), (16, 0, 1),)),
            # 15
            (u'×', ((8, 0, 1), (21, 0, 1),)),
            (u'NO', ((17, 0, 2),)),
            (u'bla', ((6, 0, 3), (18, 0, 3),)),
            (u'and', ((7, 0, 3), (19, 0, 3),)),
            (u'black', ((6, 0, 5), (18, 0, 5),)),
            # 20
            (u'wh', ((7, 4, 6), (19, 4, 6),)),
            (u'ck', ((6, 3, 5), (18, 3, 5),)),
            (u'te', ((7, 7, 9), (20, 0, 2),)),
            (u'super', ((9, 0, 5),)),
            (u'vogue', ((9, 6, 11),)),
            # 25
            (u'editorial', ((9, 12, 21),)),
            (u'feature', ((9, 22, 29),)),
            (u'and', ((7, 0, 3), (19, 0, 3),)),
            (u'white', ((7, 4, 9),)),
            (u'定價', ((4, 0, 2),)),
            # 30
            (u'NT$200', ((4, 3, 9),)),
            (u'元', ((4, 10, 11),)),
            (u'www.vogue.com.tw', ((5, 0, 16),)),
        )

        for ix, word in enumerate(preprocessor.words):
            expected = word[1]
            the(len(word.matches)).should.equal(len(expected))
            for match_ix, match in word.matches:
                the(match.index).should.equal(expected[match_ix][0])
                the(match.start).should.equal(expected[match_ix][1])
                the(match.end).should.equal(expected[match_ix][2])

    with then.each_raw_stream_should_keep_what_word_obj_compose_its_substring:

        ground_truth = (
            # 0
            (u'時尚雜誌', ((0, 0, 4),)),
            (u'國際中文版', ((1, 0, 5),)),
            (u'2012 MAY.', ((2, 0, 4), (3, 5, 9), (13, 5, 6),)),
            (u'五月號', ((4, 0, 3),)),
            (u'定價 NT$200 元', ((12, 3, 4), (29, 0, 2), (30, 3, 9), (31, 10, 11))),
            # 5
            (u'www.vogue.com.tw', ((32, 0, 16),)),
            (u'black', ((17, 0, 3), (19, 0, 5), (21, 3, 5),)),
            (u'and white', ((18, 0, 3), (20, 4, 6), (22, 7, 9), (27, 0, 3), (28, 4, 9),)),
            (u'×', ((5, 0, 1), (15, 0, 1),)),
            (u'super vogue editorial feature', ((23, 0, 5), (24, 6, 11), (25, 12, 21), (26, 22, 29),)),
            # 10
            (u'iPad', ((6, 0, 2), (7, 2, 4),)),
            (u'version now', ((8, 0, 7), (9, 8, 11),)),
            (u'UE', ((10, 0, 2),)),
            (u'W', ((11, 0, 1), (14, 0, 1),)),
            (u'N', ((12, 0, 1),)),
            # 15
            (u'M', ((13, 0, 1),)),
            (u'W', ((11, 0, 1), (14, 0, 1),)),
            (u'NO', ((12, 0, 1), (16, 0, 2),)),
            (u'black', ((17, 0, 3), (19, 0, 5), (21, 3, 5),)),
            (u'and wh', ((18, 0, 3), (20, 4, 6), (27, 0, 3),)),
            # 20
            (u'te', ((22, 0, 2),)),
            (u'×', ((5, 0, 1), (15, 0, 1),)),
            (u'\x0c', ()),
        )

        for ix, raw_stream in enumerate(preprocessor.raw_streams):
            expected = raw_stream[1]
            the(len(raw_stream.matches)).should.equal(len(expected))
            for match_ix, match in raw_stream.matches:
                the(match.index).should.equal(expected[match_ix][0])
                the(match.start).should.equal(expected[match_ix][1])
                the(match.end).should.equal(expected[match_ix][2])

    with provided.a_raw_stream_is_composed_of_non_overlapping_words:

        with and_.words_are_separated_by_spaces:

            with so.they_can_be_merged:

                may_merge_streams = (0, 1, 3, 5, 9, 10, 11, 12, 14, 15, 20,)
                for ix, raw_stream in enumerate(preprocessor.raw_streams):
                    result = ix in may_merge_streams
                    the(raw_stream.may_merge()).should.be(result)

                for ix in may_merge_streams:
                    preprocessor.raw_streams[ix].merge()

        with and_.the_words_cannot_match_other_raw_stream_anymore:

            the(preprocessor.raw_streams[2].may_merge()).should.be(True)
            the(preprocessor.raw_streams[4].may_merge()).should.be(True)
            the(preprocessor.raw_streams[17].may_merge()).should.be(True)

    with when.no_merging_can_happen_then_stop:

        page = preprocessor.run()
