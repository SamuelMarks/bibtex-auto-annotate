from collections import namedtuple
from functools import partial
from time import sleep

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import doi
from habanero import Crossref

from bibtex_auto_annotate import get_logger

log = get_logger('annotate')

cr = Crossref()


class ConnectionError(IOError):
    """A Connection error occurred."""


def annotate(record):
    """Follows visitor design-pattern to modify BibTeX records

    :param record: the record
    :type record: `dict`

    :returns the modified record
    :rtype `dict`
    """
    record = doi_from_record(record)
    if not record:
        raise TypeError('record expected to have value')
    record = doi(record)  # adds DOI url link
    return record


def try_x_times(x=5):
    def dec(f):
        def inner(record):
            attempts, failed_attempts = 0, 0
            res = None
            while attempts < x:
                try:
                    res = f(record)
                except ConnectionError as e:
                    failed_attempts += 1
                    log.exception(e)
                    log.warn('Sleeping for 30 seconds; then trying again')
                    sleep(30)
                finally:
                    attempts += 1
            if attempts == failed_attempts:
                raise ConnectionError('Reached Crossref API call limit AND retried {} times.'.format(x))
            assert res is not None
            return res

        return inner

    return dec


@try_x_times()
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
                raise ConnectionError('Reached Crossref API call limit.')
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


parser = get_bibtex_parser()

AnnotateMarshall = namedtuple('AnnotateMarshall', ('load', 'loads', 'dump', 'dumps'))(
    load=partial(bibtexparser.load, parser=parser), loads=partial(bibtexparser.loads, parser=parser),
    dumps=bibtexparser.dumps, dump=bibtexparser.dump
)
