# -*- coding: ISO-8859-1 -*-
from __future__ import print_function, absolute_import

import sys
reload(sys)
sys.setdefaultencoding('ISO-8859-1')

from argparse import Namespace
from platform import python_version_tuple
from tempfile import mkstemp
from unittest import TestCase, main as unittest_main
from os import path, remove
from codecs import open

from pkg_resources import resource_filename

from bibtex_auto_annotate.__main__ import main
from bibtex_auto_annotate.annotate import deploy_marshall, doi_from_record, try_x_times
from bibtex_auto_annotate.utils import pp, it_consumes

if python_version_tuple()[0] == '2':
    from itertools import imap, ifilter
else:
    imap = map
    ifilter = filter


class BibTeXautoAnnotateTest(TestCase):
    bibtex_samples = (
        '''
        @article{bib:Bartlett02b,
            title = "Efficient Classical Simulation of Continuous Variable Quantum Information Processes",
            author = "Stephen D. Bartlett and Barry C. Sanders and Samuel L. Braunstein and Kae Nemoto",
            year = "2002",
            journal = "Phys. Rev. Lett.",
            volume = "88",
            pages = "097904"
        }
        ''',
        '''
        @article{bib:BenjaminEisert05,
            author = "S. C. Benjamin and J. Eisert and T. M. Stace",
            title = "Optical generation of matter qubit graph states",
            year = "2005",
            journal = "New J. Phys.",
            volume = "7",
            pages = "194"
        }

        @article{bib:arxiv_1606.06821,
          title={Measurement device independent quantum key distribution over 404 km optical fibre},
          author={Yin, Hua-Lei and Chen, Teng-Yun and Yu, Zong-Wen and Liu, Hui and You, Li-Xing and Zhou, Yi-Heng and Chen, Si-Jing and Mao, Yingqiu and Huang, Ming-Qi and Zhang, Wei-Jun and others},
          eprint={arXiv:1606.06821},
          year={2016}
        }
        '''
    )

    AnnotateMarshall = deploy_marshall(retry=5)

    @staticmethod
    def has_doi_and_howpublished(entry):
        """
        :param entry: BibTeX entry
        :type entry: dict

        :returns test result, error message
        :rtype `(bool, str)`
        """
        return 'doi' in entry and 'howpublished' in entry, \
               'entry doesn\'t contain `doi` and `howpublished`. Got: {}'.format(entry)

    def test_BibDatabase_with_one_entry(self):
        parsed_entries = self.AnnotateMarshall.loads(self.bibtex_samples[0])
        pp(parsed_entries.entries)
        it_consumes(imap(lambda entry: self.assertTrue(*self.has_doi_and_howpublished(entry)),
                         parsed_entries.entries))

    def bibtex_sample_test(self, fname, rem_after=False):
        attr_name = {'quantum_internet.bib': 'full_bibtex_sample',
                     'quantum_internet.short.bib': 'short_bibtex_sample'}[fname]
        annotated_bib = mkstemp(suffix='.bib', text=True)[1]
        print('Writing processed \'{}\' out to {}'.format(fname, annotated_bib))
        with open(path.join(path.dirname(resource_filename('bibtex_auto_annotate', '__main__.py')),
                            '_data', fname), encoding='ISO-8859-1') as in_fh:
            main(Namespace(files=(in_fh,), outfile=annotated_bib, retry=15))

        with open(annotated_bib, encoding='ISO-8859-1') as out_fh:
            setattr(self, attr_name, self.AnnotateMarshall.load(out_fh))

        print('[fin] Writing processed \'{}\' out to {}'.format(fname, annotated_bib))
        it_consumes(imap(lambda entry: self.assertTrue(*self.has_doi_and_howpublished(entry)),
                         getattr(getattr(self, attr_name), 'entries')))
        print('self.{}.entries ='.format(attr_name), getattr(getattr(self, attr_name), 'entries'))
        if rem_after:
            remove(annotated_bib)

    def test_cli_full_bibtex_sample(self):
        self.bibtex_sample_test('quantum_internet.bib')

    def test_cli_short_bibtex_sample(self):
        self.bibtex_sample_test('quantum_internet.short.bib')

    def test_odd_case(self):
        entry = {
            u'title': u'Sufficient Conditions for Efficient Classical Simulation of Quantum Optics',
            u'journal': u'Phys. Rev. X',
            u'author': u'Saleh Rahimi-Keshari and Timothy C. Ralph and Carlton M. Caves',
            'ID': 'bib:SalehEffSim16', u'volume': u'6', u'year': u'2016', 'ENTRYTYPE': u'article'
        }
        pp(try_x_times(5)(doi_from_record)(entry))


if __name__ == '__main__':
    unittest_main()
