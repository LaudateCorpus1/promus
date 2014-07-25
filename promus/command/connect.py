"""Connect
Aids in the process of creating a passwordless ssh connection.

"""

import os
import sys
import pysftp
import getpass
import textwrap
import promus.core.ssh as ssh
import promus.core.git as git


DESC = """
Create a passwordless ssh connection to a remote machine. By providing
an alias for the host you create a shorcut.

example:

    promus connect user@some-server some-shortcut

you will be able to do

    ssh some-shortcut

instead of

    ssh user@some-server

"""


def add_parser(subp, raw):
    "Add a parser to the main subparser. "
    tmpp = subp.add_parser('connect',
                           help='make a passwordless ssh connection',
                           formatter_class=raw,
                           description=textwrap.dedent(DESC))
    tmpp.add_argument('host', type=str,
                      help='host to connect to')
    tmpp.add_argument('alias', type=str,
                      help='host alias')


def check_ssh_config(user, host, alias):
    """Ajust the ssh configuration file. """
    config = ssh.read_config()
    found = False
    for entry in config:
        if alias in entry.split():
            found = True
            sys.stdout.write('Alias already in use: `Host %s`\n' % entry)
            break
    if not found:
        entry = '%s %s' % (alias, host)
        config[entry] = dict()
        config[entry]['HostName'] = host
        config[entry]['User'] = user
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
    cn_ = pysftp.Connection(host,
                            username=user,
                            password=getpass.getpass())
    try:
        with cn_.open('.ssh/authorized_keys', 'r') as fp_:
            authorized_keys = fp_.read()
    except IOError:
        authorized_keys = ''
    disp = sys.stdout.write
    if key in authorized_keys:
        disp("Connection has been previously established\n")
    else:
        try:
            cn_.mkdir('.ssh')
        except IOError:
            pass
        cn_.chmod('.ssh', 700)
        if authorized_keys and authorized_keys[-1] != '\n':
            authorized_keys += '\n'
        line = "%s %s@%s\n" % (idkey,
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
            disp('You may now connect to %s using: `ssh %s`\n' % (host, alias))
