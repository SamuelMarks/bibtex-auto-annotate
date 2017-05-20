# -*- coding: ISO-8859-1 -*-
from __future__ import print_function

import sys

reload(sys)
sys.setdefaultencoding('ISO-8859-1')

from collections import deque
from itertools import islice
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4).pprint
it_consumes = lambda it, n=None: deque(it, maxlen=0) if n is None else next(islice(it, n, n), None)
