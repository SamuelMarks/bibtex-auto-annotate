from urllib import urlopen, urlencode

import feedparser


def arxiv_url_from_query(search_query):
    base_url = 'http://export.arxiv.org/api/query?'
    query = 'search_query={qs}'.format(qs=urlencode({'search_query': search_query, 'start': 0, 'max_results': 1}))

    feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
    feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

    for entry in feedparser.parse(urlopen(base_url + query).read()).entries:
        for link in entry.links:
            if link.rel == 'alternate':
                return link.href
