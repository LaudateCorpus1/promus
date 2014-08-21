"""Add

Adds a user if promus is acting as a host or adds a host if promus is
acting as a client.

"""

import os
import sys
import socket
import textwrap
import promus.core as prc
from promus.command import exec_cmd, error

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
    """Add a new host with the private key that was sent. """
    _, _, code = exec_cmd('chmod 700 %s' % arg.host)
    if code != 0:
        sys.stderr.write('ERROR: Private key `%s` not found\n' % arg.host)
        return
    pub_key = prc.get_public_key(arg.host)
    _, gitkey = prc.get_keys()
    gitkey = prc.get_public_key(gitkey)
    host = socket.gethostname()
    email = prc.config('user.email')
    master = os.environ['USER']
    master_name = prc.config('user.name')
    alias = prc.config('host.alias')
    cmd = 'ssh -i {host} {host} ' \
          '"{pub},{gitkey},{email},{master},{name},{hostname},{alias}"'
    cmd = cmd.format(host=arg.host, gitkey=gitkey, email=email,
                     master=master, name=master_name, hostname=host,
                     alias=alias, pub=pub_key[-20:])
    sys.stderr.write('Contacting %s ... \n' % arg.host)
    out, err, code = exec_cmd(cmd)
    print out
    print err
    if code != 0:
        error("ERROR: Remote did not accept the request.")
    os.remove(arg.host)
    config = prc.read_config()
    found = False
    for entry in config:
        if arg.host.replace('@', '-') in entry.split():
            found = True
            sys.stderr.write('Existing entry: `Host %s`\n' % entry)
            break
    if not found:
        _, gitkey = prc.get_keys()
        entry = '%s' % arg.host.replace('@', '-')
        config[entry] = dict()
        user, host = arg.host.split('@')
        config[entry]['HostName'] = host
        config[entry]['User'] = user
        config[entry]['IdentityFile'] = gitkey
        prc.write_config(config)
    sys.stderr.write('done...\n')


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
    """Add the new user. """
    # useremail = arg.host
    info = os.environ['SSH_ORIGINAL_COMMAND']
    pub, key, email, user, username, host, alias = info.split(',')
    sys.stderr.write('Welcome %s, please wait...\n' % username)
    users, pending, unknown = prc.read_authorized_keys()
    # Remove access from private key
    for entry in pending:
        if entry[-20:] == pub:
            pub = entry
            break
    sent_to = pending[pub][0]  # Email must match user email
    if sent_to != email:
        error("ERROR: Email mismatch, private key is not \
              being used by intended recipient.")
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
    prc.write_authorized_keys(users, pending, unknown)
    sys.stderr.write('Connection successful ...\n')
    prc.send_mail([email, prc.config('host.email')],
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
