"""Clone

Clone a existing repository.

"""

import textwrap
import promus.core as prc


DESC = """
clone an existing repository.

"""


def add_parser(subp, raw):
    "Add a parser to the main subparser. "
    tmpp = subp.add_parser('clone',
                           help='clone an existing repository',
                           formatter_class=raw,
                           description=textwrap.dedent(DESC))
    tmpp.add_argument('repo', type=str,
                      help='the repository to clone')


def run(arg):
    """Run command. """
    prc.clone(arg.repo)
