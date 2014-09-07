"""
execute a command on a host.

    ssh host cmd <==> promus exec-on host cmd

this command only exists as a reminder of this option and to be
able to see the commands available on the host.

"""

import textwrap
from promus.core import Promus


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    tmpp = subp.add_parser('exec-on',
                            help='execute a command on a host',
                            formatter_class=raw,
                            description=textwrap.dedent(__doc__))
    tmpp.add_argument('host', type=str,
                      help="host name")
    tmpp.add_argument('command', type=str,
                      help="command to execute")


def run(arg):
    """Run command. """
    print arg.host
    print arg.command
    
