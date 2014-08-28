"""Sync Utilities"""

import sys
import os.path as pth
from datetime import datetime
from six.moves import cPickle as pickle
from promus.command import exec_cmd, disp

COLOR = {
    'BD': '1',
    'R': '31',
    'G': '32',
    'Y': '33',
    'B': '34',
    'M': '35',
    'C': '36',
    'BR': '1;31',
    'BG': '1;32',
    'BY': '1;33',
    'BB': '1;34',
    'BM': '1;35',
    'BC': '1;36',
}


def c_msg(color, msg):
    """Return a message in the color specified."""
    return '\033[%sm%s\033[0m' % (COLOR[color], msg)


def c_error(msg):
    """Print a color message to the standard error stream and exit.
    """
    sys.stderr.write(c_msg('BR', 'ERROR: '))
    sys.stderr.write(c_msg('R', msg+'\n'))
    sys.exit(2)


def c_warn(msg):
    """Print a color message to the standard error stream.
    """
    sys.stderr.write(c_msg('BY', 'WARNING: '))
    sys.stderr.write(c_msg('Y', msg+'\n'))


def dump_config(config):
    """Store a sync configuration. """
    with open(pth.expanduser('~/.promus/promus-sync'), 'w') as tmp:
        pickle.dump(config, tmp)


def load_config():
    """Load a sync configuration. """
    try:
        with open(pth.expanduser('~/.promus/promus-sync'), 'r') as tmp:
            config = pickle.load(tmp)
    except IOError:
        config = list()
    return config


def print_entry(config, index):
    """Display an entry of the configuration. """
    entry = config[index]
    if entry[3] == datetime(1, 1, 1):
        sync_date = '     Never Synced     '
    else:
        sync_date = entry[3].strftime("%b/%d/%Y - %H:%M:%S")
    msg = '{lb} {index} {rb}{lb} {sync_date} {rb}'
    if entry[0] != '':
        msg += '{lb} {alias} {rb}{colon} '
    else:
        msg += '{colon} '
    msg += '{local} <==> {remote}\n'
    msg = msg.format(
        lb=c_msg('BD', '['),
        rb=c_msg('BD', ']'),
        colon=c_msg('BD', ':'),
        index=c_msg('G', index),
        sync_date=c_msg('R', sync_date),
        alias=c_msg('G', entry[0]),
        local=c_msg('C', entry[1]),
        remote=c_msg('C', entry[2]),
    )
    disp(msg)


def register(local, remote, alias):
    """Register a pair of directories to sync. """
    config = load_config()
    if not pth.isdir(local):
        c_error('"%s" does not exist in this machine.' % local)
    if local[-1] != '/':
        local += '/'
    if not pth.isdir(remote):
        tmp = remote.split(':')
        if len(tmp) == 1:
            c_error('The remote path does not exist')
        cmd = "ssh %s 'cd %s'" % (tmp[0], tmp[1])
        _, _, exit_code = exec_cmd(cmd)
        if exit_code != 0:
            c_error('Verify hostname and remote directory.')
    if remote[-1] != '/':
        remote += '/'
    config.append([alias, local, remote, datetime(1, 1, 1)])
    dump_config(config)
    entry_file = pth.expanduser('~/.promus/sync-%d.txt' % (len(config)-1))
    open(entry_file, 'w').close()
    disp(c_msg('B', 'Registration successful. \n'))
