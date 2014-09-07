"""
greet a user. This command is not meant to be used by manually.

"""

import textwrap
from promus.core import Promus


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    subp.add_parser('greet',
                    help='greet a user (server side)',
                    formatter_class=raw,
                    description=textwrap.dedent(__doc__))


def run(_):
    """Run command. """
    prs = Promus()
    prs.greet()
