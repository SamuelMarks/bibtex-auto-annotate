# -*- coding: ISO-8859-1 -*-
from __future__ import print_function

import sys

reload(sys)
sys.setdefaultencoding('ISO-8859-1')

from collections import namedtuple
from functools import partial
from platform import python_version_tuple
from time import sleep
from sys import stderr

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import doi
from habanero import Crossref

from bibtex_auto_annotate import get_logger
from bibtex_auto_annotate.arXiv import arxiv_eprint_from_query
from bibtex_auto_annotate.utils import pp

log = get_logger('annotate')

cr = Crossref()

py_ver = int(python_version_tuple()[0])


class ConnectionError(IOError):
    """A Connection error occurred."""


def annotate(retry):
    """
    
    :param retry: number of times to retry call-limited API calls
    :type retry: `int` 
    """

    def actual_annotate(record):
        """Follows visitor design-pattern to modify BibTeX records
    
        :param record: the record
        :type record: `dict`
    
        :returns the modified record
        :rtype `dict`
        """
        record = try_x_times(retry)(doi_from_record)(record)
        if not record:
            raise TypeError('record expected to have value')
        record = doi(record)  # adds DOI url link
        if 'link' in record:
            if 'url' in record['link'] and record['link']['url']:
                record['howpublished'] = '\url{' + '{}'.format(record['link']['url']) + '}'
            del record['link']
        record = eprint_from_record(record)
        pp(record)
        return record

    return actual_annotate


def try_x_times(retry):
    """
    :param retry: number of times to retry call-limited API calls
    :type retry: `int` 
    """

    def dec(f):
        def inner(record):
            attempts, failed_attempts = 0, 0
            res = None
            while attempts < retry:
                try:
                    res = f(record)
                except ConnectionError as e:
                    failed_attempts += 1
                    log.exception(e)
                    log.warn('Sleeping for 30 seconds; then trying again')
                    stderr.write('Sleeping for 30 seconds; then trying again\n')
                    sleep(30)
                finally:
                    attempts += 1
            if attempts == failed_attempts:
                raise ConnectionError('Reached Crossref API call limit AND retried {} times.'.format(retry))
            assert res is not None
            return res

        return inner

    return dec


doi_from_record_withretry = lambda r: try_x_times(r)(doi_from_record)


def doi_from_record(record):
    """Finds the DOI online (using CrossRef's API) then adds it to the record

    :param record: the record
    :type record: `dict`

    :returns the modified record
    :rtype `dict`
    """
    if 'doi' not in record:
        try:
            crossref_rec = cr.works(
                limit=1, **{'query_title': record['title']} if 'title' in record
                else {'query': ' '.join('{}'.format(v)
                                        for v in getattr(record, 'itervalues' if py_ver == 2 else 'values')())}
            )['message']['items'][0]
        except KeyError as e:
            if e.message == 'content-type':
                raise ConnectionError('Reached Crossref API call limit.')
            raise

        if 'DOI' in crossref_rec:
            record['doi'] = crossref_rec['DOI']
        if 'link' in crossref_rec and len(crossref_rec['link']) and 'URL' in crossref_rec['link'][0]:
            record['howpublished'] = '\url{' + '{}'.format(crossref_rec['link'][0]['URL']) + '}'
        elif 'link' in crossref_rec:
            print("crossref_rec['link'] was:", crossref_rec['link'])

        '''
        # Example of using the Crossref API to get a BibTeX file from the DOI:
        from habanero import cn
        bibtex = cn.content_negotiation(ids=crossref_rec['DOI'])
        '''

    return record


def eprint_from_record(record):
    """Finds the eprint online (using arXiv's API) then adds it to the record

    :param record: the record
    :type record: `dict`

    :returns the modified record
    :rtype `dict`
    """
    if 'eprint' not in record:
        try:
            if 'title' not in record:
                # TODO: DOI => title resolution
                log.warn('Not resolving eprint for this record, as title not provided:', record)
                return record
            query = 'ti:{title}{author_query}'.format(title=record['title'],
                                                      author_query='+AND+au:{author}'.format(author=record['author'])
                                                      if 'author' in record else '')
            eprint = arxiv_eprint_from_query(query)
        except UnicodeEncodeError as e:
            log.warn('{} on: {}'.format(e.__class__.__name__, record['doi'] if 'doi' in record else record))
            log.exception(e)
            eprint = None
        if eprint is not None and eprint != 'arXiv:alternate':
            record['eprint'] = eprint

    return record


def get_bibtex_parser(retry=5):
    """
    Creates a parser for rading BibTeX files
    
    :param retry: number of times to retry call-limited API calls
    :type retry: `int`

    :return: parser instantiated with `annotate` customisation
    :rtype: `BibTexParser`
    """
    _parser.customization = annotate(retry)
    return _parser


_parser = BibTexParser()

Marshall = namedtuple('Marshall', ('load', 'loads', 'dump', 'dumps'))


def deploy_marshall(retry):
    """
    Creates a parser for rading BibTeX files

    :param retry: number of times to retry call-limited API calls
    :type retry: `int`

    :return: parser instantiated with `annotate` customisation
    :rtype: `bibtex_auto_annotate.annotate.Marshall`
    """
    parser = get_bibtex_parser(retry)
    return Marshall(
        load=partial(bibtexparser.load, parser=parser), loads=partial(bibtexparser.loads, parser=parser),
        dumps=bibtexparser.dumps, dump=bibtexparser.dump
    )
