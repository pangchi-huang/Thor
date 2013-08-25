#!/usr/bin/env python

# standard library imports
import os.path

# third party related imports
from pyspecs import and_, given, it, the, then, this, when
import ujson

# local library imports
from Thor.preprocessor.raw import RawTextPreprocessor


with given.a_RawTextPreprocessor:

    with then.it_extracts_texts_in_content_stream_order:

    with then.each_word_obj_should_locate_itself_in_every_possible_raw_stream:

    with then.each_raw_stream_should_keep_what_word_obj_compose_its_substring:

    with provided.a_word_object_uniquely_composes_a_raw_stream_substring:

        with and_.there_is_only_one_possible_word_object_is_its_neighbor:

            with and_.they_are_joined_by_spaces:

                with so.they_can_be_merged:

                with so.the_mergee_is_no_longer_others_neighbor:

    with when.no_merging_can_happen_then_stop: