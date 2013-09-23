#!/usr/bin/env python

# standard library imports
import sys

# third party related imports

# local library imports
from Thor.pdf.page import PDFPage
from Thor.preprocess.fontspec import FontSpecPreprocessor
from Thor.preprocess.raw import RawTextPreprocessor
from Thor.preprocess.naive import NaivePreprocessor
from Thor.understanding.xycut import XYCut

def main(argv):

    if len(argv) != 3:
        print 'usage: python %s <PDF-File> <page-num>' % argv[0]
        exit(1)

    filename = argv[1]
    page_num = int(argv[2])

    page = PDFPage.extract_texts(filename, [page_num])[0]
    preprocessor = RawTextPreprocessor(filename, page)
    page = preprocessor.run()
    with open('raw.txt', 'wb') as f:
        f.write(page.serialize())

    preprocessor = NaivePreprocessor(filename, page)
    page = preprocessor.run()
    with open('naive.txt', 'wb') as f:
        f.write(page.serialize())

    preprocessor = FontSpecPreprocessor(filename, page)
    page = preprocessor.run()

    worker = XYCut()
    result = worker.run(page)
    out = '\n-----------------------------------------------\n'.join(result)
    print '\n\n\n'
    print out.encode('utf8')

if __name__ == '__main__':
    main(sys.argv)