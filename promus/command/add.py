"""
adds a host to your ssh configuration file and sends your public git
key.

"""

import os
import textwrap
from promus import send_mail
from promus.core import ssh
from promus.command import exec_cmd, disp, error
from promus.core.user import MASTER


def add_parser(subp, raw):
    """Add a parser to the main subparser. """
    tmpp = subp.add_parser('add', help='add a host',
                           formatter_class=raw,
                           description=textwrap.dedent(__doc__))
    tmpp.add_argument('type', type=str, metavar='TYPE',
                      choices=['host', 'user'],
                      help='One of the following: host')
    tmpp.add_argument('host', type=str,
                      help='the name of the private key sent to you')


def add_host(arg):
    """Add a new host with the private key that was sent. """
    _, _, code = exec_cmd('chmod 700 %s' % arg.host)
    if code != 0:
        error('ERROR: Private key `%s` not found\n' % arg.host)

    pub_key = ssh.get_public_key(arg.host)
    _, gitkey = ssh.get_keys()
    gitkey = ssh.get_public_key(gitkey)

    cmd = 'ssh -o "IdentitiesOnly yes" -i {host} {host} ' \
          '"{pub},{gitkey},{email},{user_name},{name},{hostname},{alias}"'
    cmd = cmd.format(host=arg.host,
                     gitkey=gitkey,
                     email=MASTER['email'],
                     user_name=MASTER['user'],
                     name=MASTER['name'],
                     hostname=MASTER['host'],
                     alias=MASTER['alias'],
                     pub=pub_key[-20:])
    disp('Contacting %s ... \n' % arg.host)
    _, _, code = exec_cmd(cmd, True)
    if code != 0:
        error("ERROR: Remote did not accept the request.\n")

    os.remove(arg.host)
    config = ssh.read_config()
    found = False
    new_entry = arg.host.replace('@', '-')
    for entry in config:
        if new_entry in entry.split():
            found = True
            disp('Existing entry: `Host %s`\n' % entry)
            break
    if not found:
        config[new_entry] = dict()
        user_name, host = arg.host.split('@')
        config[new_entry]['HostName'] = host
        config[new_entry]['User'] = user_name
        config[new_entry]['IdentityFile'] = gitkey
        config[new_entry]['IdentitiesOnly'] = 'yes'
        ssh.write_config(config)
    disp('done\n')


EMAIL_TXT = """Hello {name},

You public key has been added and you may now connect to {host} as
{user} using your public key. You may only run git and other allowed
commands however. To see which repositories you are allowed to
connect you can use the promus search command.

- Promus

"""
EMAIL_HTML = """<p>Hello {name},</p>
<p>You public key has been added and you may now connect to {host} as
{user} using your public key. You may only run git and other allowed
commands however. To see which repositories you are allowed to
connect you can use the promus search command.</p>
<p>
<strong>- Promus</strong>
</p>
"""


def add_user(_):
    """Add the new user. """
    # Retrieve guest information
    info = os.environ['SSH_ORIGINAL_COMMAND']
    pub, key, email, username, name, host, alias = info.split(',')
    disp('Welcome %s, please wait...\n' % name)
    users, pending, unknown = ssh.read_authorized_keys()

    # Remove access from private key
    for entry in pending:
        if entry[-20:] == pub:
            pub = entry
            break

    # Email must match user email
    if pending[pub][0] != email:
        error("ERROR: Email mismatch, private key is not "
              "being used by intended recipient.\n")
    del pending[pub]

    # Handle guest
    if email not in users:
        users[email] = dict()
    entry = key[-10:]
    if entry not in users[email]:
        users[email][entry] = dict()
    key_type, key_val = key.split()
    guest = users[email][entry]
    guest['user'] = username
    guest['name'] = name
    guest['alias'] = alias
    guest['host'] = host
    guest['key_type'] = key_type
    guest['key_desc'] = '%s@%s - git' % (username, alias)
    guest['key'] = key_val
    ssh.write_authorized_keys(users, pending, unknown)
    disp('Connection successful ...\n')
    send_mail([email, MASTER['email']],
              'Connection successful',
              EMAIL_TXT.format(name=name,
                               host=MASTER['host'],
                               user=MASTER['user']),
              EMAIL_HTML.format(name=name,
                                host=MASTER['host'],
                                user=MASTER['user']))


def run(arg):
    """Run command. """
    func = {
        'host': add_host,
        'user': add_user,
    }
    func[arg.type](arg)
