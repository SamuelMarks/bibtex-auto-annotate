# -*- coding: ISO-8859-1 -*-
from __future__ import print_function

import sys

reload(sys)
sys.setdefaultencoding('ISO-8859-1')

from urllib import urlopen, urlencode

import feedparser


def arxiv_eprint_from_query(search_query):
    base_url = 'http://export.arxiv.org/api/query?'
    query = urlencode({'search_query': search_query, 'start': 0, 'max_results': 1})

    feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
    feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

    for entry in feedparser.parse(urlopen(base_url + query).read()).entries:
        for link in entry.links:
            if link.rel == 'alternate':
                return 'arXiv:{}'.format(link['href'][link['href'].find('abs')+4:])
