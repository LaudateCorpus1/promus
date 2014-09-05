"""
create a passwordless ssh connection to a remote machine.

example:

    promus connect user@some-server some-shortcut

you will be able to do

    ssh some-shortcut

instead of

    ssh user@some-server

"""
import os
import pysftp
import getpass
import textwrap
from paramiko.ssh_exception import (
    BadAuthenticationType,
    AuthenticationException
)
from promus.core import git, ssh
from promus.command import disp, error


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    tmpp = subp.add_parser('connect',
                           help='make a passwordless ssh connection',
                           formatter_class=raw,
                           description=textwrap.dedent(__doc__))
    tmpp.add_argument('host', type=str,
                      help='host to connect to')
    tmpp.add_argument('alias', type=str,
                      help='host alias')


def check_ssh_config(user, host, alias):
    """Ajust the ssh configuration file. """
    config = ssh.read_config()
    rewrite = False
    if 'IdentitiesOnly' not in config['*']:
        config['*']['IdentitiesOnly'] = 'yes'
        rewrite = True
    found = False
    for entry in config:
        if alias in entry.split():
            found = True
            disp('alias already in use: `Host {0}`\n'.format(entry))
            break
    if not found:
        entry = '%s %s' % (alias, host)
        config[entry] = dict()
        config[entry]['HostName'] = host
        config[entry]['User'] = user
        rewrite = True
    if rewrite:
        ssh.write_config(config)


def run(arg):
    """Run command. """
    host = arg.host
    alias = arg.alias
    tmp = host.split('@')
    if len(tmp) == 2:
        user = tmp[0]
        host = tmp[1]
    else:
        user = os.environ['USER']
        host = tmp[0]
    idkey, _ = ssh.get_keys()
    idkey = ssh.get_public_key(idkey)
    key = idkey.split()[1]
    try:
        cn_ = pysftp.Connection(host, username=user)
    except AuthenticationException:
        try:
            cn_ = pysftp.Connection(host,
                                    username=user,
                                    password=getpass.getpass())
        except BadAuthenticationType:
            error("ERROR: unable to connect to host\n")
    try:
        with cn_.open('.ssh/authorized_keys', 'r') as fp_:
            authorized_keys = fp_.read()
    except IOError:
        authorized_keys = ''
    if key in authorized_keys:
        disp("connection has been previously established\n")
    else:
        try:
            cn_.mkdir('.ssh')
        except IOError:
            pass
        cn_.chmod('.ssh', 700)
        if authorized_keys and authorized_keys[-1] != '\n':
            authorized_keys += '\n'
        line = "{0} {1}@{2}\n".format(idkey,
                                      os.environ['USER'],
                                      git.config('host.alias'))
        authorized_keys += line
        try:
            with cn_.open('.ssh/authorized_keys', 'w') as fp_:
                fp_.write(authorized_keys)
            cn_.chmod('.ssh/authorized_keys', 700)
        except IOError:
            disp("ERROR: unable to write the authorized_keys file\n")
        finally:
            check_ssh_config(user, host, alias)
            disp('you may now connect to %s using: `ssh %s`\n' % (host, alias))
