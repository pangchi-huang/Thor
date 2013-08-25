#!/usr/bin/env python
"""
pdftext.py v1.0
Program to convert PDF to plain text with word bounding box information.

Usage:
    pdftext.py [options] <PDF-File>

Options:
    -p, --pages
        Specifies the page numbers to extract, e.g. 1,2,3 or 1-10 or 1-10,20,30.
    -d, --pagedir
        Specifies the directory to contain text json page by page.
    -o, --output
        Specifies the output filename.

"""

# standard library imports
import argparse
from contextlib import closing
import os
import os.path
import re
import subprocess
import time

# third party related imports
import ujson

# local library imports
from Thor.pdf.page import PDFPage


def create_argument_parser():
    """Create argument parser and register parameters."""

    doc_lines = __doc__.splitlines()
    parser = argparse.ArgumentParser(description=doc_lines[2])

    options_ix = doc_lines.index('Options:') + 1
    while options_ix < len(doc_lines):
        line = doc_lines[options_ix].strip()
        if line.startswith('-'):
            flags = line
            options_ix, descriptions = options_ix + 1, []
            while options_ix < len(doc_lines) and \
                  not doc_lines[options_ix].strip().startswith('-'):
                descriptions.append(doc_lines[options_ix].strip())
                options_ix += 1

            parser.add_argument(*flags.split(', '), type=str, default=None,
                                help=' '.join(descriptions))

    parser.add_argument('PDF-file')

    return parser

def parse_pages(user_input):
    """Parse user's input pages."""

    if user_input is None:
        return None

    pages = user_input.split(',')
    ret = []

    for p in pages:
        if p.isdigit():
            ret.append(int(p))
            continue

        match_obj = re.match(r'(\d+)\-(\d+)', p)
        if match_obj is None:
            continue

        start, end = match_obj.group(1), match_obj.group(2)
        ret.extend(range(int(start), int(end) + 1))

    return ret if len(ret) != 0 else None

def create_folder(folder_name):
    """Create a folder to contain every page JSON."""

    if folder_name == '':
        return None

    try:
        os.mkdir(folder_name)
    except OSError, e:
        pass

    return folder_name

def count_pages(pdf_file):
    """Returns number of pages of the specified pdf file."""

    RE_PAGES = re.compile(r'Pages:\s*(\d+)')
    pdfinfo = subprocess.check_output(('pdfinfo', pdf_file))
    match_obj = RE_PAGES.search(pdfinfo)
    return int(match_obj.group(1))

def run(input_filename, page_nums, page_dir, output_filename):

    pages = PDFPage.extract_texts(input_filename, page_nums)

    if page_dir is not None:
        for p in pages:
            output_file = os.path.join(page_dir, '%03d.json' % p.page_num)
            with closing(open(output_file, 'wb')) as f:
                f.write(p.serialize())

    output = {
        'version': int(time.time()),
        'file': input_filename,
        'page': len(pages) if page_nums is None else count_pages(input_filename),
        'data': map(lambda p: p.__json__(), pages),
    }

    with closing(open(output_filename, 'wb')) as f:
        f.write(ujson.dumps(output, ensure_ascii=False))

def main():
    """Parse arguments and bypass them to run()."""

    arg_parser = create_argument_parser()
    arg_dict = vars(arg_parser.parse_args())

    # determine what pages to be parsed
    page_nums = parse_pages(arg_dict['pages'])

    # determine whether or not to dump JSON page by page
    page_dir = arg_dict['pagedir']
    if page_dir is not None:
        page_dir = create_folder(page_dir.decode('utf8'))

    # get the input pdf file
    pdf_filename = arg_dict['PDF-file'].decode('utf8')
    pdf_filename = os.path.abspath(pdf_filename)

    # determine the output filename
    output_filename = arg_dict.get('output')
    if output_filename is None:
        basename = os.path.basename(pdf_filename)
        base, ext = os.path.splitext(basename)
        output_filename = '%s.json' % base

    run(pdf_filename, page_nums, page_dir, output_filename)


if __name__ == "__main__":

    main()
