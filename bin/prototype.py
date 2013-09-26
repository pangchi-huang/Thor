#!/usr/bin/env python

# standard library imports
from contextlib import closing
import subprocess
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

    preprocessor = NaivePreprocessor(filename, page)
    page = preprocessor.run()

    preprocessor = FontSpecPreprocessor(filename, page)
    page = preprocessor.run()

    cmd = ('pdftocairo', '-f', str(page_num), '-l', str(page_num),
           '-jpeg', '-singlefile', '-cropbox',
           '-scale-to-x', str(int(page.width)), '-scale-to-y', '-1',
           filename, 'output')
    subprocess.check_call(cmd)

    with closing(open('output.js', 'wb')) as f:
        f.write('window.pdfdata=')
        f.write(page.serialize())
        f.write(';')


if __name__ == '__main__':

    main(sys.argv)
