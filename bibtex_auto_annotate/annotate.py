from __future__ import unicode_literals
from collections import namedtuple

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import doi
from habanero import Crossref


class ConnectionError(IOError):
    """A Connection error occurred."""


cr = Crossref()


def annotate(record):
    """Follows visitor design-pattern to modify BibTeX records

    :param record: the record
    :type record: `dict`

    :returns the modified record
    :rtype `dict`
    """
    record = doi_from_record(record)
    record = doi(record)  # adds DOI url link
    return record


def doi_from_record(record):
    """Finds the DOI online then adds it to the record

    :param record: the record
    :type record: `dict`

    :returns the modified record
    :rtype `dict`
    """
    if 'doi' not in record:
        try:
            crossref_rec = cr.works(
                limit=1, **{'query_title': record['title']} if 'title' in record
                else {'query': ' '.join('{}'.format(v) for v in record.itervalues())}
            )['message']['items'][0]
        except KeyError as e:
            if e.message == 'content-type':
                raise ConnectionError('Reached Crossref API call limit. Try again later.')
            raise

        record['doi'] = crossref_rec['DOI']

        '''
        # Example of using the Crossref API to get a BibTeX file from the DOI:
        from habanero import cn
        bibtex = cn.content_negotiation(ids=crossref_rec['DOI'])
        '''

    return record


def get_bibtex_parser():
    """
    Creates a parser for rading BibTeX files

    :return: parser instantiated with `annotate` customisation
    :rtype: `BibTexParser`
    """
    parser = BibTexParser()
    parser.customization = annotate
    return parser


def load(bibtex_file):
    """
    Load :class:`BibDatabase` object from a file

    :param bibtex_file: input file to be parsed
    :type bibtex_file: `file`

    :return: bibliographic database object
    :rtype: `bibtexparser.bibdatabase.BibDatabase`
    """
    return bibtexparser.load(bibtex_file, parser=get_bibtex_parser())


def loads(bibtex_str):
    """
    Load :class:`BibDatabase` object from a string

    :param bibtex_str: input BibTeX string to be parsed
    :type bibtex_str: `str|unicode`

    :return: bibliographic database object
    :rtype: `bibtexparser.bibdatabase.BibDatabase`
    """
    return bibtexparser.loads(bibtex_str, parser=get_bibtex_parser())


AnnotateMarshall = namedtuple('AnnotateMarshall', ('load', 'loads', 'dump', 'dumps'))(
    load=load, loads=loads, dumps=bibtexparser.dumps, dump=bibtexparser.dump
)
