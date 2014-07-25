"""Show

Display information about the keys and users that have access to your
account.

"""

import os
import re
import sys
import socket
import textwrap
import promus.core.ssh as ssh
import promus.core.git as git

RE_LINE = re.compile('(?P<stuff>.*?)ssh-(?P<type>.*?) '
                     '(?P<key>.*?) (?P<desc>.*)')
DESC = """
use this command to quickly view your ssh keys or the users that are
allowed to connect to your account.

"""


def add_parser(subp, raw):
    "Add a parser to the main subparser. "
    tmpp = subp.add_parser('show', help='display account status',
                           formatter_class=raw,
                           description=textwrap.dedent(DESC))
    tmpp.add_argument('type', type=str, choices=['users', 'keys'],
                      help='information type')


def show_keys():
    """Display your public key and your git key. """
    display = sys.stdout.write
    host = socket.gethostname()
    master = os.environ['USER']
    alias = git.config('host.alias')
    id_key, git_key = ssh.get_keys()
    id_key = ssh.get_public_key(id_key)
    display('# ID_RSA:\n')
    display('%s %s@%s - %s\n' % (id_key, master, host, alias))
    git_key = ssh.get_public_key(git_key)
    display('# GIT_KEY:\n')
    display('%s %s@%s - %s - git\n' % (git_key, master, host, alias))


def show_users():
    """Display all the users that have access to your account. """
    users, pending, unknown = ssh.read_authorized_keys()
    disp = sys.stdout.write
    disp('\n')
    emails = sorted(users.keys())
    for user in emails:
        disp('  %s:\n' % user)
        for key, content in users[user].items():
            disp('    ...%s: %s, %s, %s\n' % (key[-6:], content[1],
                                              content[0], content[2]))
        disp('\n')
    keys = pending.keys()
    if keys:
        disp('There are [%d] pending requests:\n\n' % len(keys))
        data = [(key[-6:], pending[key][0]) for key in keys]
        data = sorted(data, key=lambda x: x[1])
        for item in data:
            disp('  ...%s: %s\n' % item)
        disp('\n')
    if unknown:
        msg = 'There are [%d] unknown entries in ~/.ssh/authorized_keys:\n\n'
        disp(msg % len(unknown))
        for item in unknown:
            match = RE_LINE.match(item)
            if match:
                disp('  ...%s: %s\n' % (match.group('key')[-6:],
                                        match.group('desc')))
            else:
                disp('  NO MATCH ON: ...%s\n' % item[-10:])
        disp('\n')


def run(arg):
    """Run command. """
    func = {
        'keys': show_keys,
        'users': show_users,
    }
    func[arg.type]()
