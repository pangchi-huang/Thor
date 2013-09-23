#!/usr/binenv python
# -*- coding: utf-8 -*-

# standard library imports

# third party realted imports
from pyspecs import and_, as_well_as, given, it, provided, so, the, then, this, when

# local library imports
from Thor.utils.Rectangle import Rectangle, TextRectangle


with given.a_TextRectangle:

    with provided.there_is_a_word_object:
        w = {'x': 1, 'y': 2, 'w': 3, 'h': 4, 't': u'ABC'}

        with then.it_can_be_created_directly:
            tr = TextRectangle(w['x'], w['y'], w['w'], w['h'], w['t'])
            the(tr.x).should.equal(1)
            the(tr.y).should.equal(2)
            the(tr.w).should.equal(3)
            the(tr.h).should.equal(4)
            the(tr.t).should.equal(u'ABC')

        with and_.it_can_be_created_by_calling_create_method:
            tr = TextRectangle.create(w)
            the(tr.x).should.equal(1)
            the(tr.y).should.equal(2)
            the(tr.w).should.equal(3)
            the(tr.h).should.equal(4)
            the(tr.t).should.equal(u'ABC')

        del w

    with when.it_is_classified_into_three_types_of_orientation:
        words = [
            {'x': 0, 'y': 0, 'w': 200, 'h': 100, 't': u'A'},
            {'x': 0, 'y': 0, 'w': 100, 'h': 100, 't': u'ABC'},
            {'x': 0, 'y': 0, 'w': 200, 'h': 100, 't': u'ABC'},
            {'x': 0, 'y': 0, 'w': 100, 'h': 200, 't': u'ABC'}
        ]

        with provided.only_has_single_character_or_equal_dimension:
            tr = TextRectangle.create(words[0])

            with so.its_orientation_is_unknown:
                the(tr.orientation).should.equal(tr.UNKNOWN)

        with provided.has_the_same_width_and_height:
            tr = TextRectangle.create(words[1])

            with so.its_orientation_is_unknown:
                the(tr.orientation).should.equal(tr.UNKNOWN)

        with provided.width_is_longer_than_height:
            tr = TextRectangle.create(words[2])

            with so.its_orientation_is_landscape_type:
                the(tr.orientation).should.equal(tr.LANDSCAPE)

        with provided.height_is_longer_than_width:
            tr = TextRectangle.create(words[3])

            with so.its_orientation_is_portrait_type:
                the(tr.orientation).should.equal(tr.PORTRAIT)

        del words
