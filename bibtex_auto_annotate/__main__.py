#!/usr/bin/env python

from __future__ import print_function

from functools import partial
from glob import iglob
from itertools import chain, imap
from os import path
from argparse import ArgumentParser, ArgumentTypeError, FileType
from sys import argv, exit, stderr, stdout
from codecs import open

from __init__ import __version__
from bibtex_auto_annotate.annotate import AnnotateMarshall


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
    return parser


# TODO: Get this working
def _process_glob_files(files):
    def one(f):
        _files = iglob(f)

        def nf():
            raise IOError(2, ' No such file or directory matching: {}'.format(f))

        first_file = next(_files, nf())
        for f in chain([first_file], _files):
            print('File exists: {}'.format(f))

    return tuple(imap(one, files))


def load_parse_change_emit(fh, outfile):
    with open(outfile, 'wt', encoding='ISO-8859-1') as out:
        if not hasattr(fh, 'read'):
            with open(fh, encoding='ISO-8859-1') as fh:
                AnnotateMarshall.dump(AnnotateMarshall.load(fh), out)
        else:
            AnnotateMarshall.dump(AnnotateMarshall.load(fh), out)


def main(args):
    """ Main function for CLI

    :param args:
    :type args: `argparse.Namespace`
    """
    # args.files = _process_glob_files(args.files)
    load_parse_change_emit_f = partial(load_parse_change_emit, outfile=args.outfile)
    return tuple(imap(load_parse_change_emit_f, args.files))


if __name__ == '__main__':
    _parser_args = _build_parser().parse_args()
    main(_parser_args)
