"""Greet

Greet a user. Note that this command is not meant to be used by
manually.

"""

import textwrap
import promus.core as prc


DESC = """
this command is meant to be used as a forced command over an ssh
connection.

"""


def add_parser(subp, raw):
    "Add a parser to the main subparser. "
    tmpp = subp.add_parser('greet',
                           help='greet a user',
                           formatter_class=raw,
                           description=textwrap.dedent(DESC))
    tmpp.add_argument('info', type=str,
                      help='the user information')


def run(arg):
    """Run command. """
    prs = prc.Promus()
    prs.greet(arg.info)
