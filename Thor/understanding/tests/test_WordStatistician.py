#!/usr/bin/env python

# standard library imports

# third party realted imports
from pyspecs import and_, as_well_as, given, it, provided, so, the, then, this, when

# local library imports
from Thor.understanding.stat import WordStatistician


with given.a_WordStatistician_and_supply_it_with_some_words:

    words = map(lambda i: {'x': 1. * i, 'y': 2. * i, 'w': 3. * i, 'h': 4. * i},
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