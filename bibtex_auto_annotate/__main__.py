#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
from __future__ import print_function

import sys
reload(sys)
sys.setdefaultencoding('ISO-8859-1')

from functools import partial
from glob import iglob
from itertools import chain, imap
from os import path
from argparse import ArgumentParser, ArgumentTypeError
from sys import stdout
from codecs import open

from __init__ import __version__, get_logger
from bibtex_auto_annotate.annotate import deploy_marshall

logger = get_logger('CLI')
AnnotateMarshall = None  # type: bibtex_auto_annotate.annotate.Marshall


def _build_parser():
    """
    Build argparse parser object

    :returns argparse parser object
    :rtype ArgumentParser
    """

    def extant_file(x):
        """
        'Type' for argparse - checks that file exists but does not open.
        """
        if not path.exists(x):
            # Argparse uses the ArgumentTypeError to give a rejection message like:
            # error: argument input: x does not exist
            raise ArgumentTypeError("{0} does not exist".format(x))
        return x

    parser = ArgumentParser(description='BibTeX auto annotator', version=__version__)
    parser.add_argument('-f', '--files', action='append', metavar='FILE', type=extant_file,  # type=extant_file,
                        help='One or more BibTeX files. Accepts * as wildcard for directories or filenames')
    parser.add_argument('-o', '--output-file', dest='outfile', type=str, help='Output BibTeX file', default=stdout)
    parser.add_argument('-r', '--retry', dest='retry', type=int, help='Retry times (for CrossRef API). [Default: 5]',
                        default=5)
    return parser


# TODO: Get this working
def _process_glob_files(files):
    def one(f):
        _files = iglob(f)

        def nf():
            raise IOError(2, ' No such file or directory matching: {}'.format(f))

        first_file = next(_files, nf())
        for f in chain([first_file], _files):
            logger.warn('File exists: {}'.format(f))

    return tuple(imap(one, files))


def load_parse_change_emit(marshall):
    def actual_load_parse_change_emit(fh, outfile):
        with open(outfile, 'wt', encoding='ISO-8859-1') as out:
            if not hasattr(fh, 'read'):
                with open(fh, encoding='ISO-8859-1') as in_fh:
                    marshall.dump(marshall.load(in_fh), out)
            else:
                marshall.dump(marshall.load(fh), out)

    return actual_load_parse_change_emit


def main(args):
    """ Main function for CLI

    :param args:
    :type args: `argparse.Namespace`
    """

    # AnnotateMarshall =
    # args.files = _process_glob_files(args.files)
    print (args)
    load_parse_change_emit_f = partial(load_parse_change_emit(deploy_marshall(args.retry)), outfile=args.outfile)
    return tuple(imap(load_parse_change_emit_f, args.files))


if __name__ == '__main__':
    _parser_args = _build_parser().parse_args()
    main(_parser_args)
