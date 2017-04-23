from __future__ import absolute_import, print_function

from platform import python_version_tuple
from unittest import TestCase, main as unittest_main
from os import path

from pkg_resources import resource_filename

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

    @classmethod
    def setUpClass(cls):
        cls.AnnotateMarshall = deploy_marshall(retry=5)

    @staticmethod
    def has_doi_and_link(entry):
        """
        :param entry: BibTeX entry
        :type entry: dict

        :returns test result, error message
        :rtype `(bool, str)`
        """
        return 'doi' in entry and 'link' in entry, 'entry doesn\'t contain `doi` and `link`. Got: {}'.format(entry)

    def test_BibDatabase_with_one_entry(self):
        parsed_entries = self.AnnotateMarshall.loads(self.bibtex_samples[0])
        pp(parsed_entries.entries)
        it_consumes(imap(lambda entry: self.assertTrue(*self.has_doi_and_link(entry)),
                         parsed_entries.entries))

    def test_full_bibtex_sample(self):
        with open(path.join(path.dirname(resource_filename('bibtex_auto_annotate', '__main__.py')),
                            '_data', 'quantum_internet.short.bib')) as f:
            self.full_bibtex_sample = self.AnnotateMarshall.load(f)
        parsed_entries = self.full_bibtex_sample.entries
        it_consumes(imap(lambda entry: self.assertTrue(*self.has_doi_and_link(entry)),
                         parsed_entries))

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
