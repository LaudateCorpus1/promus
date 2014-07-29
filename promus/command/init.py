"""Init

Creates a new repository.

"""

import textwrap
import promus.core as prc


DESC = """
create a new git repository in the directory ~/git. You may create a
new repository in another directory by providing the option --dir.

"""


def add_parser(subp, raw):
    "Add a parser to the main subparser. "
    tmpp = subp.add_parser('init',
                           help='create a base repository (the hub)',
                           formatter_class=raw,
                           description=textwrap.dedent(DESC))
    tmpp.add_argument('repo', type=str,
                      help='the repository name')
    tmpp.add_argument('-d', '--dir', type=str,
                      help='directory where to store the respository')


def run(arg):
    """Run command. """
    prc.init(arg.repo, arg.dir)
