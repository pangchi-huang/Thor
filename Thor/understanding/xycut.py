#!/usr/bin/env

# standard library imports
from collections import Counter

# third party related imports
import ujson

# local library imports
from Thor.pdf.page import PDFPage
from Thor.understanding.docspace import DocumentSpace, DocumentSpaceException
from Thor.utils.Rectangle import TextRectangle


class XYCut(object):

    def run(self, page):

        if len(page.words) == 0:
            return []

        root_space = DocumentSpace(map(TextRectangle.create, page.words))
        self.cut(root_space, '')

        ret = []
        root_space.traverse(ret)

        return ret

    def cut(self, space, prefix):

        if len(space.words) <= 1:
            return

        if space.reading_direction == DocumentSpace.LEFT_TO_RIGHT:
            print prefix, 'may be read from left to right'
            self._cut_left_to_right_doc(space, prefix)
        else:
            print prefix, 'may be read from top to bottom'
            self._cut_top_to_bottom_doc(space, prefix)

    def _cut_left_to_right_doc(self, space, prefix):

        vertical_cut = space.get_widest_vertical_cut(scale=0.9)

        if vertical_cut is None:
            print prefix, 'no vertical cut available'
            min_size = 2. * space.word_stat.median_height
            horizontal_cut = space.get_widest_horizontal_cut(min_size)

            if horizontal_cut is None:
                print prefix, 'no horizontal cut > %s' % min_size
                clusters = space.segment_words_horizontally()
                if len(clusters) == 1:
                    print prefix, 'there is only on ecluster, stop'
                    return

                termination = any(map(lambda c: len(c) == 1, clusters))
                if termination:
                    print prefix, 'every cluster has only one word, stop'
                    return

                subspaces = [clusters[0][:]]
                for cix in xrange(1, len(clusters)):
                    prev, curr = clusters[cix - 1], clusters[cix]

                    if  (len(curr) == len(prev) == 1) or \
                        (len(curr) > 1 and len(prev) > 1):
                        subspaces[-1].extend(clusters[cix])
                    else:
                        subspaces.append(curr[:])

                if len(subspaces) == 1:
                    print prefix, 'cannot divide itself, stop'
                    return

                space.subspaces = map(DocumentSpace, subspaces)
                for ix, subspace in enumerate(space.subspaces):
                    p = prefix + '[%s]' % ix
                    print '%s ************************************' % p
                    print ujson.dumps(map(lambda w: w.t, subspace.words), ensure_ascii=False)

                for ix, subspace in enumerate(space.subspaces):
                    p = prefix + '[%s]' % ix
                    self.cut(subspace, p)

                #map(self.cut, space.subspaces)

            else:
                space.cut_horizontally(horizontal_cut.y)
                for ix, subspace in enumerate(space.subspaces):
                    p = prefix + '[%s]' % ix
                    print '%s ************************************' % p
                    print ujson.dumps(map(lambda w: w.t, subspace.words), ensure_ascii=False)

                for ix, subspace in enumerate(space.subspaces):
                    p = prefix + '[%s]' % ix
                    self.cut(subspace, p)

                #map(self.cut, space.subspaces)


        else:
            print 'cut vertically'
            space.cut_vertically(vertical_cut.x)
            for ix, subspace in enumerate(space.subspaces):
                p = prefix + '[%s]' % ix
                print '%s ************************************' % p
                print ujson.dumps(map(lambda w: w.t, subspace.words), ensure_ascii=False)

            for ix, subspace in enumerate(space.subspaces):
                p = prefix + '[%s]' % ix
                self.cut(subspace, p)
            #map(self.cut, space.subspaces)

    def _cut_top_to_bottom_doc(self, space, prefix):

        horizontal_cut = space.get_widest_horizontal_cut(scale=0.9)

        if horizontal_cut is None:
            print prefix, 'no horizontal cut available'
            min_size = 2. * space.word_stat.median_width
            vertical_cut = space.get_widest_vertical_cut(min_size)

            if vertical_cut is None:
                print prefix, 'no vertical cut > %s' % min_size
                clusters = space.segment_words_vertically()

                termination = any(map(lambda c: len(c) == 1, clusters))
                if termination:
                    print prefix, 'every cluster has only one word, stop'
                    return

                subspaces = [clusters[0][:]]
                for cix in xrange(1, len(clusters)):
                    prev, curr = clusters[cix - 1], clusters[cix]

                    if  (len(curr) == len(prev) == 1) or \
                        (len(curr) > 1 and len(prev) > 1):
                        subspaces[-1].extend(clusters[cix])
                    else:
                        subspaces.append(curr[:])

                if len(subspaces) == 1:
                    print prefix, 'cannot divide itself, stop'
                    return

                space.subspaces = map(DocumentSpace, subspaces)
                for ix, subspace in enumerate(space.subspaces):
                    p = prefix + '[%s]' % ix
                    print '%s ************************************' % p
                    print ujson.dumps(map(lambda w: w.t, subspace.words), ensure_ascii=False)

                for ix, subspace in enumerate(space.subspaces):
                    p = prefix + '[%s]' % ix
                    self.cut(subspace, p)

                #map(self.cut, space.subspaces)

            else:
                space.cut_vertically(vertical_cut.x, left_first=False)
                for ix, subspace in enumerate(space.subspaces):
                    p = prefix + '[%s]' % ix
                    print '%s ************************************' % p
                    print ujson.dumps(map(lambda w: w.t, subspace.words), ensure_ascii=False)

                for ix, subspace in enumerate(space.subspaces):
                    p = prefix + '[%s]' % ix
                    self.cut(subspace, p)
                #map(self.cut, space.subspaces)

        else:
            space.cut_horizontally(horizontal_cut.y)
            for ix, subspace in enumerate(space.subspaces):
                    p = prefix + '[%s]' % ix
                    print '%s ************************************' % p
                    print ujson.dumps(map(lambda w: w.t, subspace.words), ensure_ascii=False)

            for ix, subspace in enumerate(space.subspaces):
                p = prefix + '[%s]' % ix
                self.cut(subspace, p)
            #map(self.cut, space.subspaces)

