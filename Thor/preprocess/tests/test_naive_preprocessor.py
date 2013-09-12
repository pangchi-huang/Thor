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
from Thor.preprocess.naive import NaivePreprocessor


with given.a_NaivePreprocessor:

    with when.it_normalizes_text_blocks_to_width_1000px:
        words = map(lambda i: {'x': 1 * i, 'y': 2 * i, 'w': 3 * i, 'h': 4 * i},
                    xrange(10))
        preprocessor = NaivePreprocessor(
            'test.pdf',
            PDFPage(page_num=1, width=200, height=200, words=words)
        )
        preprocessor._scale_words(1000 / 200.)

        with then.each_word_is_scaled_correctly:
            for ix, word in enumerate(preprocessor.words):
                the(word['x']).should.equal(5 * 1 * ix)
                the(word['y']).should.equal(5 * 2 * ix)
                the(word['w']).should.equal(5 * 3 * ix)
                the(word['h']).should.equal(5 * 4 * ix)

        del preprocessor, words


    with when.it_classifies_each_word_into_three_types_of_orientation:

        words = [
            {'x': 0, 'y': 0, 'w': 200, 'h': 100, 't': u'麗'},
            {'x': 0, 'y': 0, 'w': 100, 'h': 100, 't': u'麗寶生活家'},
            {'x': 0, 'y': 0, 'w': 200, 'h': 100, 't': u'麗寶生活家'},
            {'x': 0, 'y': 0, 'w': 100, 'h': 200, 't': u'麗寶生活家'}
        ]
        preprocessor = NaivePreprocessor(
            'test.pdf',
            PDFPage(page_num=1, width=200, height=200, words=words)
        )

        with provided.a_word_only_has_single_character_or_equal_dimension:
            word = preprocessor.words[0]

            with so.its_orientation_is_unknown:
                the(word.orientation).should.equal(word.UNKNOWN)

        with provided.a_word_has_the_same_width_and_height:
            word = preprocessor.words[1]

            with so.its_orientation_is_unknown:
                the(word.orientation).should.equal(word.UNKNOWN)

        with provided.width_is_longer_than_height:
            word = preprocessor.words[2]

            with so.its_orientation_is_landscape_type:
                the(word.orientation).should.equal(word.LANDSCAPE)

        with provided.height_is_longer_than_width:
            word = preprocessor.words[3]

            with so.its_orientation_is_portrait_type:
                the(word.orientation).should.equal(word.PORTRAIT)

        del preprocessor, words


    with as_well_as.it_has_a_text_block_factory:

        with when.it_is_supplied_with_two_words:

            words = [
                # one is landscape, the other is portrait
                {'x': 0, 'y': 0, 'w': 200, 'h': 100, 't': u'麗寶'},
                {'x': 0, 'y': 0, 'w': 100, 'h': 200, 't': u'麗寶'},
                # they are not close
                {'x': 0, 'y': 0, 'w': 200, 'h': 100, 't': u'麗寶'},
                {'x': 210, 'y': 0, 'w': 200, 'h': 100, 't': u'麗寶'},
                # they are not close
                {'x': 0, 'y': 0, 'w': 200, 'h': 100, 't': u'麗寶'},
                {'x': 0, 'y': 210, 'w': 200, 'h': 100, 't': u'麗寶'},
                # their font sizes are not close
                {'x': 0, 'y': 0, 'w': 200, 'h': 100, 't': u'aa'},
                {'x': 200, 'y': 0, 'w': 200, 'h': 120, 't': u'bb'},
                # their font sizes are not close
                {'x': 0, 'y': 0, 'w': 100, 'h': 200, 't': u'麗寶'},
                {'x': 0, 'y': 200, 'w': 120, 'h': 200, 't': u'麗寶'},

                {'x': 0, 'y': 0, 'w': 200, 'h': 100, 't': u'麗寶'},
                {'x': 200, 'y': 0, 'w': 300, 'h': 100, 't': u'生活家'},

                {'x': 0, 'y': 0, 'w': 100, 'h': 200, 't': u'麗寶'},
                {'x': 0, 'y': 200, 'w': 100, 'h': 300, 't': u'生活家'},
            ]
            preprocessor = NaivePreprocessor(
                'test.pdf',
                PDFPage(page_num=1, width=1000, height=1000, words=words)
            )
            factory = preprocessor.factory

            with provided.one_is_landscape_and_the_other_is_portrait:
                w1, w2 = preprocessor.words[0], preprocessor.words[1]

                with so.it_should_refuse_to_merge:
                    the(factory.merge(w1, w2)).should.be(None)
                    the(factory.merge(w2, w1)).should.be(None)

            with provided.the_words_are_not_close:

                with so.it_should_refuse_to_merge:
                    w1, w2 = preprocessor.words[2], preprocessor.words[3]
                    the(factory.merge(w1, w2)).should.be(None)
                    the(factory.merge(w2, w1)).should.be(None)
                    w1, w2 = preprocessor.words[4], preprocessor.words[5]
                    the(factory.merge(w1, w2)).should.be(None)
                    the(factory.merge(w2, w1)).should.be(None)

            with provided.the_font_sizes_are_not_close:

                with so.it_should_refuse_to_merge:
                    w1, w2 = preprocessor.words[6], preprocessor.words[7]
                    factory.debug = True
                    the(factory.merge(w1, w2)).should.be(None)
                    the(factory.merge(w2, w1)).should.be(None)
                    w1, w2 = preprocessor.words[8], preprocessor.words[9]
                    the(factory.merge(w1, w2)).should.be(None)
                    the(factory.merge(w2, w1)).should.be(None)

            with provided.they_can_be_merged_in_landscape_orientation:
                w1, w2 = preprocessor.words[10], preprocessor.words[11]

                with then.the_most_left_word_should_be_in_first_place:
                    the(factory.merge(w1, w2)['t']).should.equal(u'麗寶生活家')
                    the(factory.merge(w2, w1)['t']).should.equal(u'麗寶生活家')

            with provided.they_can_be_merged_in_portrait_orientation:
                w1, w2 = preprocessor.words[12], preprocessor.words[13]

                with then.the_upper_word_should_be_in_first_place:
                    the(factory.merge(w1, w2)['t']).should.equal(u'麗寶生活家')
                    print w1['t'].encode('utf8')
                    print w2['t'].encode('utf8')
                    #the(factory.merge(w2, w1)['t']).should.equal(u'麗寶生活家')


    with then.it_should_merge_as_many_words_as_possible:

        curr_dir = os.path.abspath(os.path.dirname(__file__))
        sample_json = os.path.join(curr_dir, 'fixture', 'chew_people_11.json')
        sample_pdf = os.path.join(curr_dir, 'fixture', 'chew_people_11.pdf')

        with closing(open(sample_json)) as f:
            sample = ujson.loads(f.read().decode('utf8'))

        ground_truth = [
            {"x": 145.4531, "y": 484.5423,  "w": 200,     "h": 42,        "t": u"台中秋虹谷"},
            {"x": 198.5285, "y": 529.2478,  "w": 14.8125, "h": 7.875,     "t": u"撰文"},
            {"x": 215.4635, "y": 529.2478,  "w": 2.4975,  "h": 7.875,     "t": u"I"},
            {"x": 220.0835, "y": 529.2478,  "w": 72.06,   "h": 7.875,     "t": u"萬岳乘　攝影I萬岳乘"},
            {"x": 357.4816, "y": 529.2758,  "w": 29.15,   "h": 29.15,     "t": u"被"},
            {"x": 365.9816, "y": 577.1258,  "w": 10.45,   "h": 126.7585,  "t": u"七期豪宅包圍的一窪谷地，"},
            {"x": 348.9861, "y": 577.1258,  "w": 10.45,   "h": 126.7794,  "t": u"終於成為台中市民遊蕩的中"},
            {"x": 331.9906, "y": 547.98075, "w": 10.45,   "h": 155.9558,  "t": u"心。或許鄰近百貨購物公司，帶"},
            {"x": 314.9951, "y": 547.98075, "w": 10.45,   "h": 155.9558,  "t": u"雞腿便當的、穿著窄裙與短統靴"},
            {"x": 297.9996, "y": 547.98075, "w": 10.45,   "h": 155.9558,  "t": u"的女生、背書包逃學的青年、無"},
            {"x": 281.0041, "y": 547.98075, "w": 10.45,   "h": 155.90355, "t": u"意識的肢體運動者，在最重要的，"},
            {"x": 264.0086, "y": 547.98075, "w": 10.45,   "h": 155.94535, "t": u"還有遛狗的阿公也豪邁黏著拖鞋"},
            {"x": 247.0131, "y": 547.98075, "w": 10.45,   "h": 52.25,     "t": u"散步過來。"},
            {"x": 230.0176, "y": 559.319,   "w": 10.45,   "h": 144.5862,  "t": u"這是一個安逸的市民中心，比"},
            {"x": 213.0221, "y": 547.98075, "w": 10.45,   "h": 155.9558,  "t": u"起許多冰冷堅硬的公共區域，夏"},
            {"x": 196.0266, "y": 547.98075, "w": 10.45,   "h": 155.9558,  "t": u"日烈陽曝曬，冬日寒風淒雨，光"},
            {"x": 179.0311, "y": 547.98075, "w": 10.45,   "h": 155.9558,  "t": u"禿遼闊，只為趕人與展現睥睨的"},
            {"x": 162.0356, "y": 547.98075, "w": 10.45,   "h": 155.9558,  "t": u"官威，對，我就在說台中市政府"},
            {"x": 145.0401, "y": 547.98075, "w": 10.45,   "h": 155.9558,  "t": u"前廣場，那裡最大的用途大概在"},
            {"x": 128.0446, "y": 547.98075, "w": 10.45,   "h": 135.85,    "t": u"辦法會，或大場面的告別式。"},
        ]

        preprocessor = NaivePreprocessor(
            sample_pdf,
            PDFPage(page_num=sample['page'], width=sample['width'],
                    height=sample['height'], words=sample['data'])
        )
        page = preprocessor.run()

        print ujson.dumps(page.words, ensure_ascii=False)

        the(page.page_num).should.equal(1)
        the(abs(595.28 - page.width)).should.be_less_than(1.0e-3)
        the(abs(793.7 - page.height)).should.be_less_than(1.0e-3)
        the(len(page.words)).should.equal(len(ground_truth))
        for word in page.words:
            match = False
            for truth in ground_truth:
                if word['t'] == truth['t']:
                    the(abs(word['x'] - truth['x'])).should.be_less_than(1.0e-3)
                    the(abs(word['y'] - truth['y'])).should.be_less_than(1.0e-3)
                    the(abs(word['w'] - truth['w'])).should.be_less_than(1.0e-3)
                    the(abs(word['h'] - truth['h'])).should.be_less_than(1.0e-3)
                    match = True
                    break

            the(match).should.be(True)
