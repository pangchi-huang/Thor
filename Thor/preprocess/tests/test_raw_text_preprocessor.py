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
        preprocessor = RawTextPreprocessor(
            sample_pdf,
            PDFPage.loads(f.read().decode('utf8'))
        )

    with then.it_extracts_texts_in_content_stream_order:

        raw_texts = preprocessor.page.extract_raw_texts(sample_pdf, 1)
        with closing(open(sample_raw)) as f:
            expected = f.read().decode('utf8').splitlines()

        # XXX The last raw stream is form feed, we ignore it.
        for i in xrange(22):
            the(raw_texts[i]).should.equal(expected[i])

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
            (u'vogue', ((5, 4, 9), (9, 6, 11),)),
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
            expected = ground_truth[ix][1]
            the(len(word.matches)).should.equal(len(expected))
            for match_ix, match in enumerate(word.matches):
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
            (u'www.vogue.com.tw', ((24, 4, 9), (32, 0, 16),)),
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
            expected = ground_truth[ix][1]
            the(len(raw_stream.matches)).should.equal(len(expected))
            for match_ix, match in enumerate(raw_stream.matches):
                the(match.index).should.equal(expected[match_ix][0])
                the(match.start).should.equal(expected[match_ix][1])
                the(match.end).should.equal(expected[match_ix][2])

    with provided.a_raw_stream_is_composed_of_non_overlapping_words:

        with and_.words_are_separated_by_spaces:

            with so.they_can_be_merged:

                may_merge_streams = (0, 1, 3, 9, 10, 11, 12, 14, 15, 20,)
                for ix, raw_stream in enumerate(preprocessor.raw_streams):
                    result = ix in may_merge_streams
                    the(raw_stream.may_merge()).should.be(result)

                for ix in may_merge_streams:
                    preprocessor._merge_words_of_stream(ix)

        with and_.the_words_cannot_match_other_raw_stream_anymore:

            the(preprocessor.raw_streams[2].may_merge()).should.be(True)
            the(preprocessor.raw_streams[4].may_merge()).should.be(True)
            the(preprocessor.raw_streams[5].may_merge()).should.be(True)
            the(preprocessor.raw_streams[17].may_merge()).should.be(True)

    with provided.a_raw_stream_has_overlapping_words_and_at_least_3_words:

        with then.it_should_try_to_discard_outlier_words:
            the(preprocessor.raw_streams[19].discard_outliers()).should.be(True)
            the(preprocessor.raw_streams[7].discard_outliers()).should.be(True)


    with when.no_merging_can_happen_then_stop:

        page = preprocessor.run()
        ground_truth = (
            {"y": 118.722, "x": 12.1784, "t": u"時尚雜誌", "w": 42.827, "h": 11.865},
            {"y": 130.7226, "x": 12.1784, "t": u"國際中文版", "w": 53.336, "h": 11.865},
            # '2012' + 'MAY.'
            {"y": 144.654006, "x": 12.5228, "t": u"2012 MAY.", "w": 42.9598, "h": 11.984454},
            {"y": 154.8611, "x": 12.5228, "t": u"五月號", "w": 23.504355, "h": 8.49555},
            {"y": 319.18122, "x": 487.9074, "t": u"×", "w": 29.5682, "h": 31.04661},
            # 'iP' + 'ad'
            {"y": 381.568049, "x": 533.6083, "t": u"iPad", "w": 58.700353, "h": 43.055866},
            # 'version' + 'now'
            {"y": 413.696101, "x": 515.9054, "t": u"version now", "w": 76.719667, "h": 20.978034},
            {"y": 437.181069, "x": 560.539641, "t": u"UE", "w": 0.894074, "h": 0.767728},
            {"y": 439.015641, "x": 559.871997, "t": u"W", "w": 0.894074, "h": 0.682647},
            {"y": 440.109072, "x": 559.474071, "t": u"N", "w": 0.894074, "h": 0.52179},
            {"y": 442.434193, "x": 558.627905, "t": u"M", "w": 0.894074, "h": 0.56566},
            {"y": 450.863501, "x": 555.707907, "t": u"W", "w": 0.608609, "h": 0.389801},
            {"y": 452.542475, "x": 574.8132, "t": u"×", "w": 1.0151, "h": 1.155729},
            {"y": 459.192314, "x": 552.528451, "t": u"NO", "w": 0.894074, "h": 1.048896},
            # 'bla' + 'ck'
            {"y": 458.00912, "x": 558.2718, "t": u"black", "w": 11.39622, "h": 8.522726},
            # 'and' + 'wh'
            {"y": 462.209952, "x": 557.9408, "t": u"and wh", "w": 5.549116, "h": 3.127855},
            {"y": 603.913793, "x": 143.8582, "t": u"black", "w": 331.948884, "h": 141.242165},
            {"y": 464.411419, "x": 563.989649, "t": u"te", "w": 1.517046, "h": 1.911013},
            # 'super' + 'vogue' + 'editorial' + 'feature'
            {"y": 607.500171, "x": 328.8189, "t": u"super vogue editorial feature", "w": 211.026115, "h": 16.540941},
            # 'and' + 'white'
            {"y": 717.345409, "x": 149.5275, "t": u"and white", "w": 220.371892, "h": 51.334911},
            # '定價' + 'NT$200' + '元'
            {"y": 694.9794, "x": 518.4401, "t": u"定價 NT$200 元", "w": 64.025289, "h": 12.21},
            {"y": 751.5268, "x": 518.4016, "t": u"www.vogue.com.tw", "w": 63.714, "h": 8.351},
        )

        the(page.page_num).should.equal(1)
        the(abs(page.width - 609.45)).should.be_less_than(1.0e-3)
        the(abs(page.height - 779.53)).should.be_less_than(1.0e-3)
        the(len(page.words)).should.equal(len(ground_truth))

        merged_word_map = {
            u"2012 MAY.": ground_truth[2],
            u"iPad": ground_truth[5],
            u"version now": ground_truth[6],
            u"black": ground_truth[14],
            u"and wh": ground_truth[15],
            u"super vogue editorial feature": ground_truth[18],
            u"and white": ground_truth[19],
            u"定價 NT$200 元": ground_truth[20],
        }

        for merged_word in merged_word_map:
            expected_word = merged_word_map[merged_word]
            found = False

            for word in page.words:
                if word['t'] == merged_word:
                    for attr in 'xywh':
                        print attr, word[attr], expected_word[attr]
                        the(abs(word[attr] - expected_word[attr])).\
                        should.be_less_than(1.0e-3)

                    found = True
                    break

            the(found).should.be(True)


    with when.all_words_are_aligned:
        from Thor.preprocess.raw import Stream

        ground_truth = (
            {'h': 8.50392, 'w': 22.0923, 'x': 472.494, 'y': 129.613864, 't': u'9月16日'},
            {'h': 8.50392, 'w': 22.0924, 'x': 395.675, 'y': 129.613864, 't': u'9月16日'},
            {'h': 8.50392, 'w': 22.064, 'x': 318.8703, 'y': 129.613864, 't': u'9月13日'},
            {'h': 8.50392, 'w': 22.0002, 'x': 242.0833, 'y': 129.613864, 't': u'9月12日'},
            {'h': 8.50392, 'w': 21.2846, 'x': 165.6222, 'y': 129.613864, 't': u'9月11日'},
            {'h': 8.50392, 'w': 21.1428, 'x': 88.8742, 'y': 129.613864, 't': u'9月11日'},
        )

        sample_json = os.path.join(curr_dir, 'fixture', 'test2.json')

        with closing(open(sample_json)) as f:
            preprocessor = RawTextPreprocessor(
                sample_pdf,
                PDFPage.loads(f.read().decode('utf8'))
            )
        preprocessor.raw_streams = map(Stream,
                                       map(lambda gt: gt['t'], ground_truth))
        preprocessor._associate_word_with_stream()

        with then.it_can_perform_correctly:
            page = preprocessor.run()
            the(len(page.words)).should.equal(len(ground_truth))
            for gt in ground_truth:
                match = False
                for word in page.words:
                    if abs(word['x'] - gt['x']) < 1.0e-3:
                        for attr in 'xywh':
                            the(abs(word[attr] - gt[attr])).\
                            should.be_less_than(1.0e-3)
                        the(word['t']).should.equal(gt['t'])
                        match = True
                        break

                the(match).should.be(True)

