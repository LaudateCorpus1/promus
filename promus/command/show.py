"""
use this command to quickly view your ssh keys or the users that are
allowed to connect to your account.

"""

import os
import re
import socket
import textwrap
from promus.core import git, ssh
from promus.command import disp

RE_LINE = re.compile('(?P<stuff>.*?)ssh-(?P<type>.*?) '
                     '(?P<key>.*?) (?P<desc>.*)')


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    tmpp = subp.add_parser('show', help='display account status',
                           formatter_class=raw,
                           description=textwrap.dedent(__doc__))
    tmpp.add_argument('type', type=str, choices=['users', 'keys'],
                      help='information type')


def show_keys():
    """Display your public key and your git key. """
    host = socket.gethostname()
    master = os.environ['USER']
    alias = git.config('host.alias')
    id_key, git_key = ssh.get_keys()
    id_key = ssh.get_public_key(id_key)
    disp('# ID_RSA:\n')
    disp('%s %s@%s - %s\n' % (id_key, master, host, alias))
    git_key = ssh.get_public_key(git_key)
    disp('# GIT_KEY:\n')
    disp('%s %s@%s - %s - git\n' % (git_key, master, host, alias))


def show_users():
    """Display all the users that have access to your account. """
    users, pending, unknown = ssh.read_authorized_keys()
    ssh.write_authorized_keys(users, pending, unknown)
    disp('[%d] promus users:\n\n' % len(users))
    msg = '    ...{short_key}: {name}, {user}, {alias}\n'
    users_emails = sorted(users.keys())
    for email in users_emails:
        disp('  %s:\n' % email)
        for key, guest in users[email].items():
            fmt_msg = msg.format(
                short_key=key[-10:],
                name=guest['name'],
                user=guest['user'],
                alias=guest['alias'],
            )
            disp(fmt_msg)
        disp('\n')
    keys = pending.keys()
    if keys:
        disp('[%d] pending requests:\n\n' % len(keys))
        data = [(key[-10:], pending[key][0]) for key in keys]
        data = sorted(data, key=lambda x: x[1])
        for item in data:
            disp('  ...%s: %s\n' % item)
        disp('\n')
    if unknown:
        msg = '[%d] non-promus entries in ~/.ssh/authorized_keys:\n\n'
        disp(msg % len(unknown))
        for item in unknown:
            match = RE_LINE.match(item)
            if match:
                disp('  ...%s: %s\n' % (match.group('key')[-10:],
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
