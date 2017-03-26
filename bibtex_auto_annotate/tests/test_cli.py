from __future__ import absolute_import, print_function

from contextlib import contextmanager
from itertools import imap
from tempfile import mkdtemp
from unittest import TestCase, main as unittest_main
from os import path
import sys

from shutil import rmtree

from bibtex_auto_annotate import __version__
from bibtex_auto_annotate.__main__ import _build_parser
from platform import python_version_tuple

from bibtex_auto_annotate.utils import it_consumes

if python_version_tuple()[0] == '2':
    from cStringIO import StringIO
else:
    from io import StringIO


@contextmanager
def capture_sys_output():
    capture_out, capture_err = StringIO(), StringIO()
    current_out, current_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = capture_out, capture_err
        yield capture_out, capture_err
    finally:
        sys.stdout, sys.stderr = current_out, current_err


class BibTeXautoAnnotateCliTest(TestCase):
    tmpdir = None  # type: str
    files = None  # type: (str,str,str)

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = mkdtemp(prefix='bibtex_auto_annotate_')
        cls.files = tuple(imap(lambda f: path.join(cls.tmpdir, f), ('bar.bib', 'car.bib', 'haz.bib')))
        it_consumes(imap(lambda f: open(f, 'a').close(), cls.files))

    @classmethod
    def tearDownClass(cls):
        # print('Not removing:', cls.tmpdir)
        rmtree(cls.tmpdir)

    def test_version(self):
        with self.assertRaises(SystemExit) as cm, capture_sys_output() as (stdout, stderr):
            _build_parser().parse_args('--version'.split())
        self.assertEqual(cm.exception.code, 0, stderr.getvalue())
        self.assertEqual(stderr.getvalue().rstrip('\n'), __version__)

    def test_too_many_args(self):
        with self.assertRaises(SystemExit) as cm, capture_sys_output() as (stdout, stderr):
            _build_parser().parse_args('fooo.baz {}'.format('-f'.join(self.files)).split())
        self.assertEqual(cm.exception.code, 2, stderr.getvalue())
        self.assertIn('error: unrecognized arguments', stderr.getvalue())

    def test_good_cli_args(self):
        with capture_sys_output() as (stdout, stderr):
            res = _build_parser().parse_args('-f {}'.format(' -f '.join(self.files)).split())
        self.assertItemsEqual(res.files, self.files)

    # TODO
    def _test_glob_cli_args(self):
        with capture_sys_output() as (stdout, stderr):
            res = _build_parser().parse_args('-f {dir}{sep}*'.format(dir=self.tmpdir, sep=path.sep).split())
        print(stdout.getvalue(), file=sys.stdout)
        print(stderr.getvalue(), file=sys.stderr)
        self.assertItemsEqual(res.files, self.files)


if __name__ == '__main__':
    unittest_main()
