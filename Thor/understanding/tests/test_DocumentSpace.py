#!/usr/binenv python
# -*- coding: utf-8 -*-

# standard library imports
from contextlib import closing
from itertools import product
import os.path

# third party realted imports
from pyspecs import and_, as_well_as, given, it, provided, so, the, then, this, when
import ujson

# local library imports
from Thor.pdf.page import PDFPage
from Thor.understanding.docspace import DocumentSpace
from Thor.utils.Rectangle import Rectangle, TextRectangle


with given.a_DocumentSpace:

    with then.it_can_determines_the_mainly_reading_direction:
        curr_dir = os.path.abspath(os.path.dirname(__file__))

        sample_json = os.path.join(curr_dir, 'fixture', 'test1.json')
        with closing(open(sample_json)) as f:
            sample = ujson.loads(f.read().decode('utf8'))
            words = map(TextRectangle.create, sample['data'])
            ds = DocumentSpace(words)
            the(ds.reading_direction).should.equal(DocumentSpace.LEFT_TO_RIGHT)

        sample_json = os.path.join(curr_dir, 'fixture', 'test2.json')
        with closing(open(sample_json)) as f:
            sample = ujson.loads(f.read().decode('utf8'))
            words = map(TextRectangle.create, sample['data'])
            ds = DocumentSpace(words)
            the(ds.reading_direction).should.equal(DocumentSpace.TOP_TO_BOTTOM)


    with when.it_tries_to_divide_itself_into_two_subspaces:

        words = map(TextRectangle.create, [
            {'x': 0, 'y': 0, 'w': 100, 'h': 50, 't': ''},
            {'x': 10, 'y': 100, 'w': 50, 'h': 50, 't': ''},
            {'x': 500, 'y': 0, 'w': 100, 'h': 25, 't': ''},
            {'x': 600, 'y': 100, 'w': 200, 'h': 25, 't': ''},
            {'x': 1000, 'y': 500, 'w': 100, 'h': 30, 't': ''},
            {'x': 1200, 'y': 600, 'w': 500, 'h': 30, 't': ''},
        ])
        ds = DocumentSpace(words)

        with then.it_can_enumerate_all_possible_x_cuts:
            x_cuts = ds.enumerate_vertical_cuts()
            the(x_cuts[0]).should.equal(Rectangle(100, 0, 400, 630))
            the(x_cuts[1]).should.equal(Rectangle(800, 0, 200, 630))

        with and_.it_can_choose_the_widest_one_and_divides_itself_into_2_parts:
            x_cut = ds.get_widest_vertical_cut()
            the(x_cut).should.equal(Rectangle(100, 0, 400, 630))

            with then.it_can_classify_each_word_into_a_subspace_accordingly:
                ds.cut_vertically(x_cut.x)
                the(len(ds.subspaces[0].words)).should.equal(2)
                for i in xrange(2):
                    the(words[i] in ds.subspaces[0]).should.be(True)
                    the(words[i] in ds.subspaces[1]).should.be(False)

                the(len(ds.subspaces[1].words)).should.equal(4)
                for i in xrange(2, 6):
                    the(words[i] in ds.subspaces[0]).should.be(False)
                    the(words[i] in ds.subspaces[1]).should.be(True)

        words = map(TextRectangle.create, [
            {'x': 0, 'y': 0, 'w': 100, 'h': 10, 't': ''},
            {'x': 0, 'y': 25, 'w': 100, 'h': 10, 't': ''},
            {'x': 0, 'y': 200, 'w': 100, 'h': 10, 't': ''},
        ])
        ds = DocumentSpace(words)

        with and_.it_can_enumerate_all_possible_y_cuts_as_well:
            y_cuts = ds.enumerate_horizontal_cuts()
            the(y_cuts[0]).should.equal(Rectangle(0, 10, 100, 15))
            the(y_cuts[1]).should.equal(Rectangle(0, 35, 100, 165))

        with and_.it_can_choose_the_widest_one_and_divides_itself_into_2_parts:
            y_cut = ds.get_widest_horizontal_cut()
            the(y_cut).should.equal(Rectangle(0, 35, 100, 165))

            with then.it_can_classify_each_word_into_a_subspace_accordingly:
                ds.cut_horizontally(y_cut.y)
                the(words[0] in ds.subspaces[0]).should.be(True)
                the(words[0] in ds.subspaces[1]).should.be(False)
                the(words[1] in ds.subspaces[0]).should.be(True)
                the(words[1] in ds.subspaces[1]).should.be(False)
                the(words[2] in ds.subspaces[0]).should.be(False)
                the(words[2] in ds.subspaces[1]).should.be(True)


    with when.segmenting_words:

        words = map(lambda (i, j): TextRectangle(i * 30, j * 30, 10, 10, ''),
                    product(xrange(3), repeat=2))
        ds = DocumentSpace(words)

        with provided.we_want_it_segment_words_horizontally:
            word_clusters = ds.segment_words_horizontally()

            with then.it_should_cluster_correctly:
                the(len(word_clusters)).should.equal(3)
                for i in xrange(3):
                    cluster = word_clusters[i]
                    the(len(cluster)).should.equal(3)
                    for j, w in enumerate(cluster):
                        the(w).should.equal(
                            TextRectangle(j * 30, i * 30, 10, 10, '')
                        )

        with provided.we_want_it_segment_words_vertically:
            word_clusters = ds.segment_words_vertically()

            with then.it_should_cluster_correctly:
                the(len(word_clusters)).should.equal(3)
                for i in xrange(3):
                    cluster = word_clusters[i]
                    the(len(cluster)).should.equal(3)
                    for j, w in enumerate(cluster):
                        the(w).should.equal(
                            TextRectangle((2 - i) * 30, j * 30, 10, 10, '')
                        )
