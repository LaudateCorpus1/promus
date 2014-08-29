"""Search

Search for remote repositories.

"""

import os
import sys
import socket
import textwrap
import promus.core as prc
from promus.command import exec_cmd, error, disp

DESC = """
searches for remote repositories.

"""


def add_parser(subp, raw):
    "Add a parser to the main subparser. "
    tmpp = subp.add_parser('search', help='search for repositories',
                           formatter_class=raw,
                           description=textwrap.dedent(DESC))
    tmpp.add_argument('host', type=str, nargs="?", default='',
                      help='search in the given host')

def get_accessible_repos(host):
    """Obtains a list of the accessible repos at a given host. """
    disp('Searching in: %s\n' % host)
    cmd = 'ssh %s promus-search-repos' % host
    out, err, _ = exec_cmd(cmd)
    if err.startswith('ssh'):
        disp('  ssh error: try ssh to the host manually\n\n')
    elif out == '':
        disp('  no repositories found\n\n')
    else:
        disp(out)


def run(arg):
    """Run command. """
    _, git_key =  prc.get_keys()
    config = prc.read_config()
    for alias in config:
        if arg.host not in alias:
            continue
        try:
            if config[alias]['IdentityFile'] ==  git_key:
                get_accessible_repos(alias)
        except KeyError:
            pass
