"""Add

Adds a user if promus is acting as a host or adds a host if promus is
acting as a client.

"""

import os
import sys
import socket
import textwrap
import promus.core.ssh as ssh
import promus.core.git as git
import promus.core.util as util

DESC = """
adds a host to your ssh configuration file and sends your public git
key.

"""


def add_parser(subp, raw):
    "Add a parser to the main subparser. "
    tmpp = subp.add_parser('add', help='add a host',
                           formatter_class=raw,
                           description=textwrap.dedent(DESC))
    tmpp.add_argument('type', type=str, metavar='TYPE',
                      choices=['host', 'user'],
                      help='One of the following: host')
    tmpp.add_argument('host', type=str,
                      help='the name of the private key sent to you')


def add_host(arg):
    """Display your public key and your git key. """
    disp = sys.stdout.write
    try:
        util.exec_cmd('chmod 700 %s' % arg.host, True)
    except OSError:
        disp('ERROR: Private key `%s` not found\n' % arg.host)
        return
    pub_key = ssh.get_public_key(arg.host)
    print pub_key
    _, gitkey = ssh.get_keys()
    gitkey = ssh.get_public_key(gitkey)
    host = socket.gethostname()
    email = git.config('user.email')
    master = os.environ['USER']
    master_name = git.config('user.name')
    alias = git.config('host.alias')
    cmd = 'ssh -i {host} {host} ' \
          '{pub},{gitkey},{email},{master},{name},{hostname},{alias}'
    cmd = cmd.format(host=arg.host, gitkey=gitkey, email=email,
                     master=master, name=master_name, hostname=host,
                     alias=alias, pub=pub_key[-20:])
    util.exec_cmd(cmd, True)
    os.remove(arg.host)
    config = ssh.read_config()
    found = False
    for entry in config:
        if arg.host.replace('@', '-') in entry.split():
            found = True
            disp('Existing entry: `Host %s`\n' % entry)
            break
    if not found:
        _, gitkey = ssh.get_keys()
        entry = '%s' % arg.host.replace('@', '-')
        config[entry] = dict()
        user, host = arg.host.split('@')
        config[entry]['HostName'] = host
        config[entry]['User'] = user
        config[entry]['IdentityFile'] = gitkey
        ssh.write_config(config)


EMAIL_TXT = """Hello {name},

You public key has been added and you may now connect to {host} as
{user} using your public key. You may only run git commands however.

- Promus

"""
EMAIL_HTML = """<p>Hello {name},</p>
<p>You public key has been added and you may now connect to {host} as
{user} using your public key. You may only run git commands however.
</p>
<p>
<strong>- Promus</strong>
</p>
"""


def add_user(_):
    """Display all the users that have access to your account. """
    # useremail = arg.host
    info = os.environ['SSH_ORIGINAL_COMMAND']
    pub, key, email, user, username, host, alias = info.split(',')
    users, pending, unknown = ssh.read_authorized_keys()
    # Remove access from private key
    for entry in pending:
        if entry[-20:] == pub:
            pub = entry
            break
    del pending[pub]
    if email not in users:
        users[email] = dict()
    key_type, key_val = key.split()
    content = [user,
               username,
               alias,
               key_type,
               '%s@%s' % (user, host)]
    users[email][key_val] = content
    ssh.write_authorized_keys(users, pending, unknown)
    # if useremail != email:
    # Needs to modify message if the emails do not match
    util.send_mail([email, git.config('host.email')],
                   'Connection successful',
                   EMAIL_TXT.format(name=username,
                                    host=socket.gethostname(),
                                    user=os.environ['USER']),
                   EMAIL_HTML.format(name=username,
                                     host=socket.gethostname(),
                                     user=os.environ['USER']))


def run(arg):
    """Run command. """
    func = {
        'host': add_host,
        'user': add_user,
    }
    func[arg.type](arg)
