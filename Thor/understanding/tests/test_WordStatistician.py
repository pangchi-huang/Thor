#!/usr/bin/env python

# standard library imports
import random

# third party realted imports
from pyspecs import and_, as_well_as, given, it, provided, so, the, then, this, when

# local library imports
from Thor.understanding.stat import WordStatistician
from Thor.utils.Rectangle import TextRectangle


with given.a_WordStatistician_and_supply_it_with_some_words:

    words = map(lambda i: TextRectangle(x=1.*i, y=2.*i, w=3.*i, h=4.* i, t=u''),
                xrange(10))
    ws = WordStatistician(words)

    with then.it_can_count_how_many_words_totally:
        the(ws.count).should.equal(10)

    with and_.it_can_calculate_average_width_of_textual_objects:
        the(abs(ws.avg_width - 3. * 4.5)).should.be_less_than(1.0e-3)

    with and_.it_can_calculate_average_height_of_textual_objects:
        the(abs(ws.avg_height - 4. * 4.5)).should.be_less_than(1.0e-3)

    with and_.it_can_calculate_variance_of_width_of_textual_objects:
        the(abs(ws.var_width - 3. * 3. * 8.25)).should.be_less_than(1.0e-3)

    with and_.it_can_calculate_variance_of_height_of_textual_objects:
        the(abs(ws.var_height - 4. * 4. * 8.25)).should.be_less_than(1.0e-3)

    with and_.it_can_calculate_median_of_width_of_textual_objects:
        words = [
            TextRectangle(x=0, y=0, w=1, h=1, t=u''),
            TextRectangle(x=0, y=0, w=2, h=1, t=u''),
        ]
        ws = WordStatistician(words)
        the(ws.median_width).should.equal((1 + 2) / 2.)

        words.append(TextRectangle(x=0, y=0, w=3, h=1, t=u''))
        ws = WordStatistician(words)
        the(ws.median_width).should.equal(2)

    with and_.it_can_calculate_median_of_height_of_textual_objects:
        words = [
            TextRectangle(x=0, y=0, w=1, h=1, t=u''),
            TextRectangle(x=0, y=0, w=1, h=2, t=u''),
        ]
        ws = WordStatistician(words)
        the(ws.median_height).should.equal((1 + 2) / 2.)

        words.append(TextRectangle(x=0, y=0, w=1, h=3, t=u''))
        ws = WordStatistician(words)
        the(ws.median_height).should.equal(2)


    words, horizontal_count, vertical_count = [], 0, 0
    for i in xrange(100):
        direction = random.randint(0, 2)
        if direction == 0:
            words.append(TextRectangle(x=0, y=0, w=1, h=1, t='A'))
        elif direction == 1:
            words.append(TextRectangle(x=0, y=0, w=random.randint(50, 100),
                                       h=random.randint(10, 30), t=u'ABC'))
            horizontal_count += 1
        else:
            words.append(TextRectangle(x=0, y=0, w=random.randint(10, 30),
                                       h=random.randint(50, 100), t=u'ABC'))
            vertical_count += 1
    ws = WordStatistician(words)


    with and_.it_can_count_how_many_words_are_in_landscape_orientation:
        the(ws.horizontal_word_count).should.equal(horizontal_count)

    with and_.it_can_count_how_many_words_are_in_portrait_orientation:
        the(ws.vertical_word_count).should.equal(vertical_count)